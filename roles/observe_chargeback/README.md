observe_chargeback
=========

Test chargeback in Openstack

Requirements
------------

Role Variables
--------------

  For chargeback_tests.yml

    chargeback_test_id
      - polarion id for test
    chargeback_user_list
      - List of users to check for resource usage

Dependencies
------------

Openstack on Openshift deployed and telemetry enabled for Openstack.

Example Playbook
----------------

Each tasks/playbook.yml should be called independently via "ansible.builtin.import_role" with appropriate vars passed:

- name: "Verify chargeback reporting"
  hosts: controller
  gather_facts: no
  vars:
    chargeback_user_list:
      - "user1"
      - "user2"

  tasks:
    - name: "Verify chargeback data"
      ansible.builtin.import_role:
        name: observe_chargeback


License
-------

Apache 2

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
