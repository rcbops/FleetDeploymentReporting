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

* #### 1.5 [Software Development Lifecycle (SDLC) Definition](#software-development-lifecycle)

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

* #### 1.7 [Secure Coding Guidelines](#secure-coding-guidelines)

    * Definition: Guidelines by which to develop and review code to ensure security
    * Activities:
        - Create and agreee upon guidelines for producing code
        - Research common guidelines and agree upon a subset which will apply to specific project
        - Document means of enforcing guidelines
    * Deliverables:
        - Documentation of guidelines

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

* #### 3.1 [Design & Tech Specifications](#design--tech-specifications)

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

* #### 4.3 [Unit Test](#unit-test)

    * Definition: Automation gets pull request code and runs tests 
    * Activities:
        - CI/CD system runs unit test job
    * Deliverables:
        - Passing checks on github

* #### 4.4 [Review Failing Test Results](#review-failing-test-results)

    * Definition: Test results should be long lasting and backed up
    * Activities:
        - CI/CD system should saves test logs
        - Developer or peer reviews failures from unit tests
        - Developer fixes issues and pushes to pull request
    * Deliverables:
        - Logs from test runs
        - Bug fixes within PR

* #### 4.2 [Code Review](#code-review)

    * Definition: Peers review code and approve or requeset changes/discussion
    * Activities:
        - Team member who is not code author reads through code
        - Ensure clarity and ease of understanding
        - Deploy code to dev environment and attempt to find issues
        - Consider and bring up security issues
    * Deliverables:
        - Github reviews and comments 

* #### 4.5 [Incremental Review](#incremental-review)

    * Definition: Loop through development cycle until unit tests pass and peer approval achieved 
    * Activities:
        - Continue from start of development cycle
    * Deliverables:
        - Code merged into development branch

#### 5 [Testing/Integration](#testingintegration)

* #### 5.1 [Build and Release to Development](#build-and-release-to-development)

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

<!-- /TOC -->


<!-- The preceding TOC was generated with Atom's markdown-toc plugin -->

# Inception


## Operations & Maintenance

#### RACI

## Software Development Lifecycle

#### High Level SDLC

![](images/SDLC.png)

#### Code Change Review Process

![](images/code_change_review_process.png)

    Figure 2: Flow for handling code changes via pull requests and reviews (PCI 6.3.2)


## SDLC Tools

- Jira
    * Project management
    * Feature descriptions, designs and requirements discussions
- Jenkins
    * Automation for building, testing and deployment
- Django testing framework
    * Testing for web application
- Vagrant (subject to change)
    * Infrastructure provisioning for development and testing environments
- Ansible
    * Configuration management automation for green field deploys and upgrades
- Github
    * Source code management
    * Code review discussions
- Logging ?
- Security Testing ?
- RS Monitoring
- Slack


# Planning

## Vision and Scope Specification

Each change will have a corresponding Kanban card with description.
[Cloud Snitch Jira](https://rpc-openstack.atlassian.net/secure/RapidBoard.jspa?rapidView=123)

Each should describe some subset of the following:

    * Goals & Intentions
    * Scope & Feasibility
    * Resources & Limits
    * Cost/Time to Deliver
    * Risks
    * Additional Benefits
    * Project Plan
    * Milestones
    * Additional Links

# Design

## Design & Tech Specifications

Architecture of the FleetDeploymentReporting Tool is as follow:

![](images/architecture.png)

Tech specifications for new features can be added as bullet points and/or links whiteboard images in the corresponding Kanban card.
[Cloud Snitch Jira](https://rpc-openstack.atlassian.net/secure/RapidBoard.jspa?rapidView=123)

Update sections with changes to following as it is relevant.

#### Design
- [Architecture & Diagram changes](#)
- [Development Models](#)

#### Tech Specifications
- [APIs](#api)
- [Storage](#storage)
- [Security](#security)


## Functional and Structural Test Plans

[Web App Backend Tests](https://github.com/rcbops/FleetDeploymentReporting/tree/develop/cloud_snitch/tests)

- Django testing framework
- Cover basic models and functionality of the web application


## Impact, Capacity and Monitoring

Alerts signalling errors or failures will be set up via (ALERT TECHNOLOGY?) and send messages to the Cloud Snitch development and operations team slack channel. They must be reviewed, communicated and handled according to the RACI documentation.

(INSERT TABLE OF ALERTS, RESPONSES AND SEVERITY)

In order to meet load requirements of end users the capacity should be increased/decreased according to the following chart.

(INSERT TABLE OF METRICS AND REQUIRED CAPACITY)

#### Monitoring

We will monitor trends in the following:

- latency in milliseconds of wait time

- traffic in requests per second

- errors in requests per second

- saturation as queue depth in celery requests and potentially database connections


We will alert when services are unreachable or the error rate increases. Specific rates and percentiles are yet to be determined.

## Release Plan

- Release to be scheduled once a month.
- Update all dependencies to latest versions
- Upgrades to be done in a manner that allows 
- Versioning schema. Semantic versioning with addition of a digit to represent Jenkins build number:
    * a - major (incremented when you make incompatible API changes)
    * b - minor (incremented when you add functionality in a backwards-compatible manner)
    * c - revision (incremented when you make backwards-compatible bug fixes)
    * d - build (incremented by automation system i.e. Jenkins)


## Training Plan

## Review Plans

All Cloud Snitch operations and developments team members must review documentation and send pull request to that affect once a year.
(Implement strategy to accomplish this. Comments on changelog PR?)

# Development

## Submit Code Changes

- Develop and test changes locally before opening a pull request to "develop" branch on central repository
- Check current pull request here [Snitch Github PRs](#https://github.com/rcbops/FleetDeploymentReporting/pulls)
- Determine versioning changes that need to be made according to versioning schema in [release plan](#release-plan)

## Unit Test

- Automation (Jenkins) takes pull request and uses python virtual environment to install python dependencies
- Jenkins runs unit tests against code itself without full deployment

## Review Failing Test Results

- Test results can be seen from the "Details" link when Jenkins reports failures
- Code owner must review failing tests and discover problems within new or testing system
- Peers may optionally review tests to assist debugging
- Code owner must push bug fix pull request and allow re-run of unit tests 

## Code Review

- Peer code reviewers must review code and ensure coding guidelines are followed
- Test changes locally to best of ability
- Code developer must respond to comments and/or requests for changes

## Incremental Review

- Loop through this Development phase until all unit tests pass and approval from peers

# Testing/Integration

## Build and Release to Development

- Jenkins gets all code that has been merged into develop branch
- Jenkins uses provisioning system to create new development environment
- Jenkins sets up inventory and everything to prepare for ansible run
- Ansible uses newly created development environment and deploys new code
- Ansible creates configuration files and dependencies
- Ansbile starts services, ensure all components have endpoint locations and dynamic data

## Run Second Round of Tests and Merge to Master

- Use new development environment to run tests against
- Tests shoud include
    * Unit tests
    * Functional Tests
    * Component Tests
    * Fuzz tests
    * Static analysis
    * Property based tests
    * Coverage tests
    * Benchmark tests
    * Aggression tests
    * Contract tests
    * Lint tests
    * Acceptance tests
    * Mutation tests
    * Smoke tests
    * UI/UX tests
    * Usability tests
    * Penetration tests
    * Threat modelling
    * Integration tests

## Release to QA

- Upgrade QA environment with new code
- Ensure upgrade process works as expected
- Check ansible, application and service logs for immediate errors

## Execute Long Term Tests Plans

- Use QA Tests for longer term tests
    * Tap compare
    * Network monitoring
    * Load tests
    * Shadowing
    * Config tests

## Training Doc

- Update training documentation for any plans

## User Acceptance and Training

# Deployment

## Deploy to Production

- Deploy code to virtual machines in the production environment
- Provide beta users optional access to new production environment
- Provide developer users mandatory access to new production enviornment

## Release Approval

- Allow tests to run against production workload on pre-release production environment
    * Canarying
    * Monitoring
    * Traffic shaping
    * Feature flagging
    * Exception tracking
- Receive feedback and approval from beta and developer users

## Release to Production

- Change over all production load balancers
- Provide messages to users

## Confirm Release

- Tests within released environment
    * Teeing
    * Profiling
    * Logs/events
    * Chaos testing
    * Monitoring
    * A/B Tests
    * Tracing
    * Dynamic Exploration
    * Real user monitoring
    * Auditing
    * Oncall experience

# Maintenance

## Monitor, Resolve and Mitigate Issues

- Deploy each month
    * Allow patching updates
- Watch the following dependencies for all available security patches and deploy within 1 month of release (PCI 6.2)
    * (List of dependencies)


# Operations & Maintenance



