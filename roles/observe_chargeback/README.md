Ansible Playbook: CloudKitty ChargeBack Validation
=========

This Ansible playbook validates and enforces the configuration of the OpenStack CloudKitty (chargeback) service. It performs a series of tests to ensure that the CloudKitty rating modules are in the correct state and that the `hashmap` module has the correct priority.

Playbook Files
---------

* **`main.yml`**: The main playbook entry point. It includes the `chargeback_tests.yml` file to execute the validation logic.
* **`chargeback_tests.yml`**: This task file contains the sequence of steps used to validate and configure the CloudKitty service.

Workflow
---------

The `chargeback_tests.yml` playbook executes the following steps:

1.  **Get Module Status**: It first runs the `{{ openstack_cmd }} rating module list` command to fetch the current status of all CloudKitty rating modules.

2.  **Validate Module States**: It uses an `assert` task to test for specific, expected conditions. The playbook will **fail** if these are not met:
    * The `noop` module must be **enabled** (`True`).
    * The `hashmap` module must be **enabled** (`True`).
    * The `pyscripts` module must be **disabled** (`False`).

3.  `Check Hashmap Priority`: It runs a shell command to find the current priority value of the `hashmap` module.

4.  `Set Hashmap Priority`: It idempotently sets the `hashmap` module's priority to `100`. This task is skipped if the priority is already set to `100`.



Requirements
---------

This playbook relies on an Ansible variable, `openstack_cmd`, which must be defined when running the playbook.

This variable must contain the full command necessary to execute OpenStack CLI commands (e.g., `/usr/bin/openstack` or simply `openstack` if it's in the system's PATH).
The host running the playbook must have access to the OpenStack environment and the necessary credentials loaded for the CLI to function.


Usage
---------

You can run this playbook using the `ansible-playbook` command. You must pass the `openstack_cmd` variable as an extra argument.

Example of running the playbook in bash shell:
``ansible-playbook main.yml -e "openstack_cmd=/usr/bin/openstack``


Author Information
------------------

Alex Yefimov
