# cloud_snitch
Gathers information from an osa cloud

### How to install

The following steps assume you are on the deployment host (typically ingest-01).

1. Clone rpc-uam to /opt/rpc-uam

```
git clone git@github.com:rcbops/rpc-uam.git /opt/rpc-uam
```

2. Clone FDR to /opt/FleetDeploymentReporting
```
git clone git@github.com:rcbops/FleetDeploymentReporting.git /opt/FleetDeploymentReporting
```

3. Configure ansible to use FDR's version-controlled inventory
```
cp /opt/FleetDeploymentReporting/ansible.cfg.example /etc/ansible/ansible.cfg
```

4. Select the appropriate inventory based on the environment (e.g. `aaronslab` or `kronos`) by uncommenting it in `/etc/ansible/ansible.cfg`
```
sed -i '/^#.*kronos/s/^#//' /etc/ansible/ansible.cfg
```

### How to run
```shell
# From the cloud_snitch repo directory
openstack-ansible snitch.yml
```

cloud_snitch.rc.example contains some example environment variables that enable the cloud_snitch plugins and configure where local data is stored.(likely to change)

modules in the modules directory should have symlinks in the osa ansible plugin library directory.

example:
```shell
 ln -s <path to repo>/cloud_snitch/modules/pkg_snitch.py /etc/ansible/roles/plugins/library/pkg_snitch
```

Current modules:
 - pkg_snitch
 - pip_snitch(coming soon)
