First pass at SDLC Documentation for internal use. Sections will be exported to PCI Documentation
Not all sections in Table of Contents will be used, required or accurate.

<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->



# Overview

#### 1. [Scope of this Document](#scope-of-this-document)


# Process Specification

#### 1 [Inception](#inception)

* #### 1.1 [Concept Proposal](#concept-proposal)

* #### 1.2 [Prototyping](#prototyping)

* #### 1.3 [Roles & Requirements](#roles--requirements)

* #### 1.4 [Operations & Maintenance](#operations--maintenance)

* #### 1.5 [SDLC Definition](#the-full-sdlc)

* #### 1.6 [SDLC Tools](#sdlc-tools)

#### 2 [Planning](#planning)

* #### 2.1 [Vision & Scope Specification](#vision--scope-specification)
(Dev Priorities)

* #### 2.4 [Design & Tech Specifications](#tech-specifications)

* #### 2.6 [Training Plan](#process-step-training-plan)

* #### 2.7 [Functional and Structural Test Plans](#functional--structural-test-plans)

* #### 2.8 [Impact, Capacity and Monitoring](#impact-capacity-and-monitoring)

* #### 2.9 [Release Plan](#release-plan)
    (Upgrade plans/schedules, Patch windows)

* #### 2.10 [Review Plans](#review-plans)
    (Proliferating information to teams. Read docs a year)

#### 3 [Develop](#develop)
(TODO: Daniel)

* #### 3.1 [Submit Code Changes](#write-code)

* #### 3.2 [Unit Test](#unit-test)

* #### 3.3 [Collect Unit Test Results](#collect-unit-test-results)

* #### 3.4 [Incremental Review](#incremental-review)

#### 4 [QA](#qa)

* #### 4.1 [Code Review](#code-review)

* #### 4.2 [Build](#build)

* #### 4.3 [Release to Development](#release-to-development)

* #### 4.4 [Release to QA](#release-to-qa)

* #### 4.5 [Execute Test Plans](#execute-test-plans)

* #### 4.6 [Training Doc](#training-doc)

* #### 4.7 [User Acceptance and Training](#user-acceptance-training)

#### 5 [Deploy](#deploy)

* #### 5.1 [Release Approval](#release-approval)

* #### 5.2 [Release to Production](#release-to-production)

* #### 5.3 [Confirm Release](#confirm-release)

* #### 5.4 [Project Metrics](#project-metrics)

#### 6 [Rapid SDLC Patterns](#rapid-sdlc-patterns)

* #### 6.1 [SDLC for Content Modifications and Tasks](#sdlc-for-content-modifications-and-tasks)

* #### 6.2 [SDLC for Production Data Change](#sdlc-for-production-data-change)

* #### 6.3 [SDLC for Release Management Wrapper](#sdlc-for-release-management-wrapper)

* #### 6.4 [SDLC for Research](#sdlc-for-research)

#### 7 [Other Process Patterns](#other-process-patterns)

* #### 7.1 [Process Pattern for Account](#process-pattern-for-account)


# Deliverables


#### Operations & Maintenance Deliverables (Satisfy [1.4](#operations--maintenance))

- #### 1.4.1 [Monitoring](#monitoring)
- #### 1.4.2 [RACI](#raci)

#### SDLC Definition Deliverables (Satisfy [1.5](#sdlc-definition))

- #### 1.5.1 [SDLC Diagram and Process](#sdlc-diagram-and-process)

#### SDLC Tooling Deliverables (Satisfy [1.6](#sdlc-tooling))

- #### 1.6.1 [Jenkins](#jenkins)
- #### 1.6.2 [Ansible](#ansible)
- #### 1.6.3 [RS Monitoring](#rs-monitoring)
- #### 1.6.4 [Slack](#slack)

#### Vision & Scope Specification Deliverables (Satisfy [2.1](#vision--scope-specification))

- #### 2.1.1 [Goals & Intentions](#deliverable-goals--intentions)
- #### 2.1.2 [Scope & Feasibility](#deliverable-scope--feasibility)
- #### 2.1.3 [Resources & Limits](#deliverable-resources--limits)
- #### 2.1.4 [Cost/Time to Deliver](#deliverable-costtime-to-deliver)
- #### 2.1.5 [Risks](#deliverable-risks)
- #### 2.1.6 [Additional Benefits](#deliverable-additional-benefits)

#### Project Plan Deliverables (Satisfy [2.2](#project-plan))

- #### 2.2.1 [Project Plan](#deliverable-project-plan)
- #### 2.2.2 [Milestones](#deliverable-milestones)
- #### 2.2.3 [Additional Links](#deliverable-additional-links)
- #### 2.2.4 [Changelog](#deliverable-changelog)

#### Design Deliverables (Satisfy [2.4](#design))

- #### 2.4.1 [Analysis & Requirements](#deliverable-analysis-requirements)
- #### 2.4.2 [Architecture & Diagrams](#deliverable-architecture--diagrams)
- #### 2.4.3 [Development Models](#deliverable-development-models)
- #### 2.4.4 [Versioning & Release Scheme](#deliverable-versioning--release-scheme)

#### Tech Specification (Satisfy [2.5](#tech-specification)

- #### 2.5.1 [APIs](#deliverable-apis)
- #### 2.5.2 [Storage](#deliverable-storage)
- #### 2.5.3 [Security](#deliverable-security)
(END TODO: Daniel)

<!-- /TOC -->


<!-- The preceding TOC was generated with Atom's markdown-toc plugin -->


# Planning


## Goals & Intentions

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce risus orci, tincidunt et ipsum posuere, ultrices pharetra ligula. Ut bibendum sollicitudin neque sit amet eleifend. Etiam vitae nunc erat. Aliquam luctus neque dui, a molestie arcu efficitur quis. Nulla facilisi. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam semper tortor ut tristique rutrum. Mauris nec erat et libero congue auctor porta scelerisque sapien. Quisque ac fermentum turpis. Nunc turpis magna, ornare nec porta et, fringilla ut risus.


## Scope & Feasibility

 Aliquam at orci ullamcorper, venenatis lectus id, iaculis nulla. Praesent fringilla nisi at felis eleifend euismod at sodales nibh. Phasellus eleifend ligula turpis, id malesuada risus dictum sit amet. Nunc elementum eros dolor, aliquam rhoncus elit luctus quis. Aliquam a neque fringilla, vulputate neque sit amet, maximus elit. Suspendisse potenti. Nunc faucibus, turpis id pellentesque convallis, nulla elit imperdiet lectus, at pretium libero urna a sapien.


## Resources & Limits

 Etiam et porta libero. Pellentesque libero leo, dignissim sed ipsum non, ultricies ultrices leo. Curabitur mollis maximus leo eu elementum. Morbi et dui dictum, semper justo et, rhoncus elit. Donec sollicitudin quis tellus vel tristique. Phasellus vehicula volutpat massa ac interdum. Etiam vel mattis tortor. Morbi cursus velit ex.


## Cost/Time to Deliver

 In et arcu at eros semper semper et vitae magna. Fusce ullamcorper dolor ut urna lobortis varius. Nam velit elit, tempor a viverra at, scelerisque in arcu. Maecenas fermentum libero ac est mollis, sit amet viverra massa gravida. Vestibulum viverra ante ac lectus scelerisque bibendum. Integer scelerisque, tellus porta sagittis maximus, enim erat lacinia est, eu viverra mauris odio a mauris. Nulla sagittis, lacus eu cursus mollis, mauris turpis accumsan erat, vitae tristique tortor nibh eget turpis. Etiam turpis ligula, ornare a lectus id, iaculis consectetur nulla.

## Risks

Donec cursus consectetur leo. Pellentesque mattis, tortor eu sollicitudin porta, magna ante laoreet purus, et tincidunt libero orci eget erat. Nullam et blandit est. Maecenas volutpat, sem molestie hendrerit consequat, nisl massa tincidunt neque, ac cursus enim nunc vel metus.

## Additional Benefits

 In et arcu at eros semper semper et vitae magna. Fusce ullamcorper dolor ut urna lobortis varius. Nam velit elit, tempor a viverra at, scelerisque in arcu. Maecenas fermentum libero ac est mollis, sit amet viverra massa gravida. Vestibulum viverra ante ac lectus scelerisque bibendum. Integer scelerisque, tellus porta sagittis maximus, enim erat lacinia est, eu viverra mauris odio a mauris. Nulla sagittis, lacus eu cursus mollis, mauris turpis accumsan erat, vitae tristique tortor nibh eget turpis. Etiam turpis ligula, ornare a lectus id, iaculis consectetur nulla.

# Analysis & Requirements


## Architecture & Diagrams

 Etiam et porta libero. Pellentesque libero leo, dignissim sed ipsum non, ultricies ultrices leo. Curabitur mollis maximus leo eu elementum. Morbi et dui dictum, semper justo et, rhoncus elit. Donec sollicitudin quis tellus vel tristique. Phasellus vehicula volutpat massa ac interdum. Etiam vel mattis tortor. Morbi cursus velit ex.


## Development Models

 Donec cursus consectetur leo. Pellentesque mattis, tortor eu sollicitudin porta, magna ante laoreet purus, et tincidunt libero orci eget erat. Nullam et blandit est. Maecenas volutpat, sem molestie hendrerit consequat, nisl massa tincidunt neque, ac cursus enim nunc vel metus. Sed in bibendum diam. Morbi in congue mauris. Donec vel magna a urna sagittis ultricies. Sed consequat ornare tristique. Aliquam tempor est vel ligula hendrerit, eu placerat leo ullamcorper. Nulla pellentesque eros ut lacus mollis, ac posuere mauris tempor. Nullam rutrum semper posuere. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer id felis libero.

## APIs


## Versioning & Release Scheme

 Aliquam at orci ullamcorper, venenatis lectus id, iaculis nulla. Praesent fringilla nisi at felis eleifend euismod at sodales nibh. Phasellus eleifend ligula turpis, id malesuada risus dictum sit amet. Nunc elementum eros dolor, aliquam rhoncus elit luctus quis. Aliquam a neque fringilla, vulputate neque sit amet, maximus elit. Suspendisse potenti. Nunc faucibus, turpis id pellentesque convallis, nulla elit imperdiet lectus, at pretium libero urna a sapien.


## Security

Authentication is an area we need to work with UAM on, but we intend on implementing the following security components:

- token authentication, shared with UAM.

- SSL certificates from Rackspace certs

- DNS name to a proper domain in rpc.rackspace.com, mirrored in application name headers.

- Audit log of all changes and identity of authors.

- Restricted infrastructure operations to external team than developers

- No encryption at rest should be needed, as the data secrets are already in other systems. This only stores locations to retrieve secure data.

- No disclosure data is stored (personal/medical records)


## Project Plan

## Milestones

## Additional Links

## Changelog


# Operations & Maintenance


## Monitoring

We will monitor trends in the following:

- latency in milliseconds of wait time

- traffic in requests per second

- errors in requests per second

- saturation as queue depth in celery requests and potentially database connections


We will alert when services are unreachable or the error rate increases. Specific rates and percentiles are yet to be determined.



## RACI
