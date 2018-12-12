from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64
import os

from ansible.plugins.action import ActionBase

try:
    from pwsafe.comp import PasswordSafeComp
    _pwsafe_found = True
except ImportError:
    _pwsafe_found = False


class ActionModule(ActionBase):

    # Map config keys to environment names
    env_config_map = {
        'sso_username': 'SSO_USERNAME',
        'sso_password': 'SSO_PASSWORD'
    }

    # New password size
    size = 32

    def new_password(self):
        """Generate a new base64 encoded password.

        :returns: New password
        :rtype: str
        """
        return base64.b64encode(os.urandom(self.size)).decode('utf-8')

    def get_env_config(self):
        """Get password safe configuration from environment vars.

        :returns: Configuration
        :rtype: dict
        """
        config = {}
        for py_var_name, env_var_name in self.env_config_map.items():
            val = os.environ.get(env_var_name)
            if val is None:
                raise ValueError(
                    'Missing required environment configuration for {}'
                    .format(env_var_name)
                )
            config[py_var_name] = val
        return config

    def run(self, tmp=None, task_vars=None):
        """Run the new version."""

        result = super(ActionModule, self).run(tmp, task_vars)
        result.update(changed=False)

        # Check if pwsafe import was successful.
        if not _pwsafe_found:
            result.update(
                failed=True,
                msg="Please install the pwsafe library to continue."
            )
            return result

        try:
            config = self.get_env_config()
        except ValueError as e:
            result.update(failed=True, msg=str(e))
            return result

        # project id and credential id should come as arguments.
        argument_msg = 'Argument \'{}\' is required.'
        required_args = [
            'project_id',
            'credential_id'
        ]
        for arg in required_args:
            val = self._task.args.get(arg)
            if val is None:
                result.update(failed=True, msg=argument_msg.format(arg))
                return result
            config[arg] = val

        # Generate new password from u random
        new_password = self.new_password()

        # Get existing credential
        client = PasswordSafeComp(
            config['sso_username'],
            config['sso_password']
        ).client

        # Make sure the credential exists
        try:
            resp = client.get_cred(
                config['project_id'],
                config['credential_id']
            )
            resp.raise_for_status()
            cred = resp.json()
            result.update(exists_status_code=resp.status_code, cred=cred)
        except Exception as e:
            result.update(failed=True, msg=str(e))
            return result

        # Update existing credential
        try:
            resp = client.update_cred(
                config['project_id'],
                config['credential_id'],
                password=new_password
            )
            resp.raise_for_status()
            result.update(
                update_status_code=resp.status_code,
                new_password=new_password,
                project_id=config['project_id'],
                credential_id=config['credential_id']
            )
        except Exception as e:
            result.update(failed=True, msg=str(e))

        return result
