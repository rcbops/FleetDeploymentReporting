First pass at SDLC Documentation for internal use. Sections will be exported to PCI Documentation
Not all sections in Table of Contents will be used, required or accurate.

<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->


# Process Specification

#### 1 [Inception](#inception)

* #### 1.1 [Concept Proposal](#concept-proposal)
    
    * Definition: Brief, informal discussion/description of the proposed product, feature or design change
    * Activities: 
        - Discussion/Description of the following
        - Use case discussion
        - Business implication discussions
        - Externalities to the project i.e. dependencies, affected parties

* #### 1.2 [Prototyping](#prototyping)

    * Definition: Produce working prototype that can be demoed.
    * Activities:
        - Update or create code in github
        - Deploy new code to development environment.
        - Add enough test data/infrastructure to perform a demo
    * Deliverables:
        - New code in github
        - Short-lived demo deployment

* #### 1.3 [Roles & Requirements](#roles--requirements)

    * Definition: Define roles of team members and requirements of product 
    * Activities:
        - Determine roles and expectations of managers, developers, operators and users
        - Define process and requirements for disseminating project information   
    * Deliverables:
        - RACI
        - System to require/remind team members to review documentation

* #### 1.4 [Operations & Maintenance](#operations--maintenance)

    * Definition: Process and design of system(s) that facilitate secure, reliable and long term deployments
    * Activities:
        - Document steps to deploy, migrate, scale and debug
        - Define processes for handling alerts and escalation
    * Deliverables:
        - Operations Documentation
        - Implement notification and communication paths

* #### 1.5 [Software Development Lifecycle (SDLC) Definition](#the-full-sdlc)

    * Definition: Documentation describing the SDLC
    * Activities:
        - Determine the requirements of the project and limitations of the tools/environments
        - Design SDLC
    * Deliverables:
        - SDLC diagram and description

* #### 1.6 [SDLC Tools](#sdlc-tools)

    * Definition: Documentation of the tools required for the SDLC
    * Activities:
        - Find all tools used within the SDLC
    * Deliverables:
        - Table with name and description of tooling

#### 2 [Planning](#planning)

* #### 2.1 [Vision & Scope Specification](#vision--scope-specification)

    * Definition: Description and discussion of project updates
    * Activities:
        - Summarize the update and it's purpose
        - Add priority to summary
        - Set status of update
        - Discuss relevant research, discoveries or changes to requirements
    * Deliverables:
        - Kanban card(s)

#### 3 [Design](#design)

* #### 3.1 [Design & Tech Specifications](#tech-specifications)

    * Definition: Diagrams and outlines of changes to be made
    * Activities:
        - Create high level solutions
        - Whiteboard, discuss and adjust solution
        - Small first pass at code
        - Determine other software or teams to involve
        - Discover required data sources
        - Consider security implications and solutions
    * Deliverables:
        - Diagrams/implementation plan or first pass of code
        - Notes/comments or emails for other teams to contact

* #### 3.2 [Functional and Structural Test Plans](#functional-and-structural-test-plans)

    * Definition: Plans on how to test various aspects of the new solution
    * Activities:
        - Determine test framework
        - Understand types of tests and possible pitfalls
        - Create tests that define acceptance criteria for new code
    * Deliverables:
        - Documentation of any new testing frameworks or processes
        - Tests in codebase

* #### 3.3 [Impact, Capacity and Monitoring](#impact-capacity-and-monitoring)

    * Definition: Define monitors to create, how and when to handle capacity based on monitors and impact to end users and operations
    * Activities:
        - Define the metrics to determine capacity
        - Determine ranges that require scaling up or down
        - Create alerts and response processes
    * Deliverables:
        - Alert/response documentation

* #### 3.4 [Release Plan](#release-plan)

    * Definition: Define plans for upgrades, schedules for releases and patch windows
    * Activities:
        - Define release schedules
        - Create process for updating project to new versions
        - Create process for patching operating systems and dependencies
        - Define upgrade plans via configuration management tools
    * Deliverables:
        - Documentation for release schedules, patches and updates

* #### 3.5 [Training Plan](#training-plan)

    * Defition: Outlines for creating and holding training sessions 
    * Activites:
        - Produce training guide frameworks
        - Create process to schedule training for operators and users
    * Deliverables:
        - Training doc frameworks
        - Training scheduling process

* #### 3.6 [Review Plans](#review-plans)

    * Definition: Plan to disseminate information and documentation
    * Activities:
        - Decide how often team members must review documenatation for compliance
    * Deliverables:
        - Documentation of team member requirements

#### 4 [Development](#develop)

* #### 4.1 [Submit Code Changes](#write-code)

    * Definition: Developers produce code and send off for review
    * Activities:
        - Create and test new code in development environment
        - Send PR to development branch of main repository
    * Deliverables:
        - Pull Request

* #### 4.2 [Code Review](#code-review)

    * Definition: Peers review code and approve or requeset changes/discussion
    * Activities:
        - Team member who is not code author reads through code
        - Ensure clarity and ease of understanding
        - Deploy code to dev environment and attempt to find issues
        - Consider and bring up security issues
    * Deliverables:
        - Github reviews and comments 

* #### 4.3 [Unit Test](#unit-test)

    * Definition: Automation gets pull request code and runs tests 
    * Activities:
        - CI/CD system runs unit test job
    * Deliverables:
        - Passing checks on github

* #### 4.4 [Collect Unit Test Results](#collect-unit-test-results)

    * Definition: Test results should be long lasting and backed up
    * Activities:
        - CI/CD system should save test logs
        - Backup for 
    * Deliverables:
        - Logs from test runs
        - Storage for backups and older logs

* #### 4.5 [Incremental Review](#incremental-review)

    * Definition: Loop through development cycle until unit tests pass and peer approval achieved 
    * Activities:
        - Continue from start of development cycle
    * Deliverables:
        - Code merged into development branch

#### 5 [Testing/Integration](#testing-integration)

* #### 5.1 [Build](#build)

    * Definition: Automation retrieves and builds peer approved and unit tested code from development branch 
    * Activities:
        - Create code artifacts and/or images
        - Install up-to-date dependencies to ensure security and compatability
    * Deliverables:
        - Code artifacts/Images

* #### 5.2 [Release to Development and Run Second Round of Tests](#release-to-development)

    * Definition: Create development environment and install code
    * Activities:
        - Create short-lived environment for second round of testing
        - Run green-field installation code
    * Deliverables:
        - Test logs
        - Master branch with new code after successful deploy and test
        - Environment of failed deploy/test

* #### 5.3 [Release to QA](#release-to-qa)

    * Notes: Would be great if we could test upgrade paths via old images or just deploying versions and testing upgrades
    * Definition: Send code to environment with more accurate data to run long lived tests and load tests
    * Activities:
        - Upgrade QA environment to new version
        - Ensure data migrations worked
        - Enable monitoring
    * Deliverables:
        - Monitoring alerts
        - Environment location

* #### 5.4 [Execute Long Term Tests Plans](#execute-long-term-test-plans)

    * Definition: Run tests and close-to-production workloads against QA environment
    * Activities:
        - test workloads, repeat close-to-production input
        - Run security tests
    * Deliverables:
        - Test results
        - Alerts
        - Responses to issues

* #### 5.5 [Training Doc](#training-doc)

    * Definition: Create training documentation for new features or products
    * Activities:
        - Document information necessary for both users and operations based on templates
    * Deliverables:
        - Training documentation

* #### 5.6 [User Acceptance and Training](#user-acceptance-training)

    * Definition: Provide beta versions to users or demos. Train users on new features/products
    * Activities:
        - Deploy a beta version to get user feedback
        - Implement required changes by starting from planning stage
        - Schedule training sessions
    * Deliverables:
        - Beta environment or demo
        - User feedback
        - Training sessions

#### 6 [Deployment](#deploy)

    * #### 6.1 [Release Approval](#release-approval)

        * Definition: Allow users, operations and developers to approve new releases. Security issues may bypass users and operations
        * Activities:
            - Schedule release/patch window
            - Talk to everyone affected to gain agreement
        * Deliverables:
            - Approval via discussion

    * #### 6.2 [Release to Production](#release-to-production)

        * Definition: Upgrade code in environment via rollout or in-place upgrade 
        * Activities:
            - Backup current data and environments
            - During scheduled windows run upgrade scripts
            - Notify users, operations and developers when release complete
        * Deliverables:
            - Notifications to users, operations and developers
            - Upgraded production environment

    * #### 6.3 [Confirm Release](#confirm-release)

        * Definition: Consider user, operational and monitoring feedback and be ready to rollback 
        * Activities:
            - Read all comments, alerts and concerns
            - Rollback if major issues arise

#### 7 [Maintenance](#maintenance)

    * #### 7.1 [Monitor, Resolve and Mitigate Issues](#monitor-resolve-and-mitigate-issues)

        * Definition: Monitor and update system to ensure system runs securely and smoothly 
        * Activities:
            - Respond to monitoring alerts within appropriate timeframes
            - Start patch/upgrade processes when vulnerabilities discovered


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
