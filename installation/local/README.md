## Infrastructure related playbooks

This section covers playbooks used to configure the instances where FDR runs.

### Prerequisites

1. Install ansible role dependencies

```
ansible-galaxy install -r ansible_requirements.yml
```

2. All infrastructure instances are members of the `fdr_infra` group.
:warning: Until we work out how inventory will be managed under version control, this step needs to be performed manually. :warning:

Example inventory:

```
[cloud_snitch_sync]
ingest-01

[web]
web-01

[neo4j]
neo4j-01

[jump]
jump-01

[fdr_infra:children]
cloud_snitch_sync
web
neo4j
jump
```

3. The variables in `group_vars/fdr_infra.yml` have been added to the appropriate location.
:warning: Until we work out how inventory will be managed under version control, these variables need to be kept up to date manually. :warning:

### Playbooks

 - `infrastructure.yml` - includes all of the following playbooks in this section
 - `ansible-hardening.yml` - apply the [ansible-hardening](https://github.com/openstack/ansible-hardening/) role

## Application components

TBD - not sure on the order or prerequisites for these

## Neo4J Graph DB Tier

TBD

## Sync Tier

TBD

## Web Tier

TBD
