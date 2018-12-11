## Infrastructure related playbooks

This section covers playbooks used to configure the instances where FDR runs.

### Prerequisites

1. Install ansible role dependencies

```
ansible-galaxy install -r ansible_requirements.yml
```

### Playbooks

 - `infrastructure.yml` - includes all of the following playbooks in this section
 - `ansible-hardening.yml` - apply the [ansible-hardening](https://github.com/openstack/ansible-hardening/) role
 - `splunk.yml` - install and configure Splunk [as specified](https://one.rackspace.com/display/gss/Splunk+PCI+Playbook) by the SAAC team

## Application components

TBD - not sure on the order or prerequisites for these

## Neo4J Graph DB Tier

TBD

## Sync Tier

TBD

## Web Tier

TBD
