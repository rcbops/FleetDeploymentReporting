import time
from cloud_snitch.sync import sync_single

from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    """Runs sync on collected data locally.

    Requires argumments uuid and key
    """

    def run(self, tmp=None, task_vars=None):
        """Run the action plugin.

        :param uuid: Uuid of a collection run. Should indicate a set of data
            at path /path/to/data/dir/<uuid>.tar.gz
        :type uuid: str
        :param key: Base64 encode encryption key
        :type key: str
        """
        # Init the result
        result = super(ActionModule, self).run(tmp, task_vars)
        result.update(changed=False)

        # Start the elapsed time measurement.
        start = time.time()
        try:
            if self._task.args.get('uuid') is None:
                raise ValueError('Argument \'uuid\' is required.')
            if self._task.args.get('key') is None:
                raise ValueError('Argument \'key\' is required.')
            path = '/etc/cloud_snitch/data/{}.tar.gz'
            path = path.format(self._task.args['uuid'])
            sync_single(path, key=self._task.args['key'])
        except Exception as e:
            msg = 'Unable to sync run at path \'{}\': {}'.format(path, e)
            result.update(failed=True, msg=msg)
        finally:
            result.update(elapsed=time.time() - start)
        return result
