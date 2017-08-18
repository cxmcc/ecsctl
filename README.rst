ecsctl
======

kubectl-style command line tool for AWS EC2 Container Services (ECS)

Installation
------------

.. code:: bash

    pip install ecsctl

Purpose
-------

A convenient command line tool to view ECS cluster status and do
troubleshooting.

This tool is trying to provide similar functionality of ``kubectl`` for
kubernetes.

Of course, ECS and kubernetes are so different. Many features on
kubernetes are not possible here in ECS.

Some AWS official projects to check out:

-  `ecs-cli <http://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_installation.html>`__
-  `aws-cli ecs
   command <http://docs.aws.amazon.com/cli/latest/reference/ecs/>`__

Usage
-----

Cluster
^^^^^^^

List nodes:

::

    % ecsctl get clusters
    NAME     STATUS      RUNNING    PENDING    INSTANCE COUNT
    default  ACTIVE            3          0                 2

Get cluster details:

::

    % ecsctl describe cluster mycluster

Create/delete cluster:

::

    % ecsctl create cluster mycluster

Container Instances (nodes)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

List nodes:

::

    % ecsctl get nodes --cluster mycluster
    INSTANCE ID                           EC2 INSTANCE ID      STATUS      RUNNING COUNT
    00000000-1111-2222-3333-444444444444  i-abcdef123456abcde  ACTIVE                  1

Get node detail:

::

    % ecsctl describe node 00000000-1111-2222-3333-444444444444

Drain/undrain node:

::

    % ecsctl drain 00000000-1111-2222-3333-444444444444

Services
^^^^^^^^

List services:

::

    % ecsctl get services

List services in certain order:

::

    % ecsctl get services --sort-by "createdAt"

Delete a service:

::

    % ecsctl delete service badservice

Delete a service (even if it has desiredCount > 0):

::

    % ecsctl delete service badservice --force

Run container quick start
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    % ecsctl run mycontainer --image busybox
    mycontainer

    % ecsctl get services
    NAME             TASK DEFINITION      DESIRED    RUNNING  STATUS    AGE
    mycontainer-svc  mycontainer:1              1          0  ACTIVE    10 seconds ago

Run docker exec on containers (Requires customizing docker daemon to listen on internal addresses)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    % ecsctl get tasks
    TASK ID                               STATUS    TASK DEFINITION    AGE
    42f052c4-80e9-411d-bea2-407b0b4a4b0b  PENDING   mycontainer:1      2 minutes ago

    % ecsctl exec 42f052c4-80e9-411d-bea2-407b0b4a4b0b date
    Fri May 26 00:13:24 PDT 2017

    % ecsctl exec -it 42f052c4-80e9-411d-bea2-407b0b4a4b0b /bin/bash
    root@container:/# (interactive)

Configure docker daemon to allow ``ecsctl exec``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Let docker daemon listen on TCP ports (required)

Add options like ``-H tcp://0.0.0.0:MYDOCKERPORT`` or environment
variable ``DOCKER_HOST=tcp://0.0.0.0:MYDOCKERPORT`` to configure docker
daemon. See `dockerd
documentation <https://docs.docker.com/engine/reference/commandline/dockerd/#daemon-socket-option>`__
for more information.

2. Security enhancement: dropping traffic from ECS containers to docker
   daemon.

   ::

       iptables --insert INPUT 1 --in-interface docker+ --protocol tcp --destination-port MYDOCKERPORT --jump DROP

Configs
^^^^^^^

Set default cluster name (equivalent to ``--cluster`` option)

::

    % ecsctl config set cluster mycluster

Set default docker daemon port

::

    % ecsctl config set docker_port 2375
