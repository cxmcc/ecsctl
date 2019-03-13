
import click
from .alias import AliasedGroup
from . import wrapboto
from .config import read_config, update_config, default_config
from . import display
from .pty import Pty
from .ssh import Ssh
import tabulate
import datetime
import pytz
import humanize
import os
import time
from jsonpath import jsonpath as jp


TASK_DEFINITION_STATUS = ['ACTIVE', 'INACTIVE', 'ALL']


@click.group()
@click.pass_context
def cli(ctx):
    for k, v in read_config().items():
        if k in ctx.obj:
            ctx.obj[k] = v
    ctx.obj['bw'] = wrapboto.BotoWrapper()


@cli.group(short_help='Manage config file.')
def config():
    pass


@config.command(name='set')
@click.argument('key', type=click.Choice(default_config))
@click.argument('value')
@click.pass_context
def config_set(ctx, key, value):
    update_config(key, value)


@config.command(name='show')
def config_show():
    click.echo(read_config())


@cli.group(cls=AliasedGroup,
           short_help='Create resources.')
def create():
    pass


@create.command(name='cluster')
@click.argument('name', required=True)
@click.pass_context
def create_cluster(ctx, name):
    bw = ctx.obj['bw']
    resp = bw.create_cluster(name)
    click.echo(resp['clusterArn'])


@cli.group(cls=AliasedGroup, short_help='Delete resources.')
def delete():
    pass


@delete.command(name='service')
@click.option('--cluster')
@click.option('--force', is_flag=True, default=False,
              help='Scale down count to 0 before deleting.')
@click.option('--raw-response', default=False, show_default=True)
@click.argument('service', required=True)
@click.pass_context
def delete_service(ctx, service, cluster, force, raw_response):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    resp = bw.delete_service(service, cluster=cluster, force=force)
    if raw_response:
        click.echo(display.de_unicode(resp['service']))
    else:
        click.echo(resp['service']['serviceArn'])


@delete.command(name='cluster')
@click.argument('cluster', required=True)
@click.pass_context
def delete_cluster(ctx, cluster):
    bw = ctx.obj['bw']
    resp = bw.delete_cluster(cluster)
    click.echo(resp['clusterArn'])


@delete.command(name='task-definition')
@click.argument('task-definition', required=True)
@click.pass_context
def delete_task_definition(ctx, task_definition):
    bw = ctx.obj['bw']
    resp = bw.deregister_task_definition(task_definition)
    click.echo(resp['taskDefinitionArn'])


@cli.group(cls=AliasedGroup,
           short_help=('Show details of a specific '
                       'resource or group of resources'))
def describe():
    pass


@describe.command(name='service')
@click.option('--cluster')
@click.argument('service', required=True)
@click.pass_context
def describe_services(ctx, service, cluster):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    service = bw.describe_service(cluster=cluster, service=service)
    output = display.de_unicode(service)
    click.echo(output)


@describe.command(name='container-instance')
@click.option('--cluster')
@click.argument('node', required=True)
@click.pass_context
def describe_node(ctx, node, cluster):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    node = bw.describe_container_instance(node, cluster=cluster)
    output = display.de_unicode(node)
    click.echo(output)


@describe.command(name='task-definition')
@click.option('--cluster')
@click.option('--data-only', is_flag=True, default=False)
@click.argument('task-definition', required=True)
@click.pass_context
def describe_task_definitions(ctx, task_definition, cluster, data_only):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    info = bw.describe_task_definition(task_definition, cluster=cluster)
    if data_only:
        info = bw.strip_task_def_data(info)
    output = display.de_unicode(info)
    click.echo(output)


@describe.command(name='task')
@click.option('--cluster')
@click.argument('task', required=True)
@click.pass_context
def describe_tasks(ctx, task, cluster):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    info = bw.describe_task(task, cluster=cluster)
    output = display.de_unicode(info)
    click.echo(output)


@describe.command(name='cluster')
@click.argument('cluster', required=True)
@click.pass_context
def describe_cluster(ctx, cluster):
    bw = ctx.obj['bw']
    info = bw.describe_cluster(cluster)
    output = display.de_unicode(info)
    click.echo(output)


@cli.command(short_help='Drain node in preparation for maintainence.')
@click.option('--cluster')
@click.argument('node', required=True)
@click.pass_context
def drain(ctx, node, cluster):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    resp = bw.drain_node(node, cluster=cluster)
    click.echo(resp['containerInstances'][0]['containerInstanceArn'])


@cli.command(short_help='Undrain node back into active status.')
@click.option('--cluster')
@click.argument('node', required=True)
@click.pass_context
def undrain(ctx, node, cluster):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    resp = bw.undrain_node(node, cluster=cluster)
    click.echo(resp['containerInstances'][0]['containerInstanceArn'])


@cli.command(name='ssh', short_help='Execute a command in a container via ssh.')
@click.option('--cluster')
@click.option('--container', default=None)
@click.option('--user', default=None)
@click.option('--ssh-port', default=22, type=int)
@click.argument('task', required=True)
@click.argument('command')
@click.pass_context
def ssh_command(ctx, task, command, cluster, ssh_port,
                 container, user):
    if not cluster:
        cluster = ctx.obj['cluster']
    if not ssh_port:
        ssh_port = int(ctx.obj['ssh_port'])
    if not user:
        if 'ECS_USER' in os.environ:
            user = os.environ.get('ECS_USER')
        else:
            user = os.environ.get('USER')
    bw = ctx.obj['bw']
    ssh = Ssh(bw=bw, task=task, command=command, cluster=cluster,
              port=ssh_port, user=user, container=container)
    ssh.exec_command()

@cli.command(name='exec', short_help='Execute a command in a container.')
@click.option('--cluster')
@click.option('-i', '--stdin', is_flag=True, default=False, show_default=True)
@click.option('-t', '--tty', is_flag=True, default=False, show_default=True)
@click.option('--container', default=None)
@click.option('--docker-port', type=int)
@click.option('--docker-api-version')
@click.argument('task', required=True)
@click.argument('command', nargs=-1)
@click.pass_context
def exec_command(ctx, task, command, stdin, tty, cluster, docker_port,
                 docker_api_version, container):
    if not cluster:
        cluster = ctx.obj['cluster']
    if not docker_port:
        docker_port = int(ctx.obj['docker_port'])
    if not docker_api_version:
        docker_api_version = ctx.obj['docker_api_version']
    bw = ctx.obj['bw']
    pty = Pty(bw=bw, task=task, command=command, cluster=cluster,
              tty=tty, stdin=stdin, port=docker_port,
              api_version=docker_api_version,
              container=container)
    pty.exec_command()


@cli.group(cls=AliasedGroup, short_help='Display one or many resources.')
def get():
    pass


@get.command(name='cluster')
@click.option('--sort-by')
@click.pass_context
def get_clusters(ctx, sort_by):
    bw = ctx.obj['bw']
    records = bw.get_clusters()
    if sort_by:
        records.sort(key=lambda r: jp(r, sort_by))
    out = []
    for r in records:
        status = r['status']
        name = r['clusterName']
        running_count = r['runningTasksCount']
        pending_count = r['pendingTasksCount']
        instance_count = r['registeredContainerInstancesCount']
        row = (name, status, running_count, pending_count, instance_count)
        out.append(row)
    headers = ['NAME', 'STATUS', 'RUNNING', 'PENDING', 'INSTANCE COUNT']
    output = tabulate.tabulate(out, headers=headers, tablefmt='plain')
    click.echo(output)


@get.command(name='service')
@click.option('--cluster')
@click.option('--sort-by')
@click.pass_context
def get_services(ctx, cluster, sort_by):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    records = bw.get_services(cluster=cluster)
    if sort_by:
        records.sort(key=lambda r: jp(r, sort_by))
    out = []
    now = datetime.datetime.now(pytz.utc)
    for r in records:
        service_name = r['serviceName']
        task_def = display.simple_task_definition(r['taskDefinition'])
        status = r['status']
        created_at = r['createdAt']
        desired_count = r['desiredCount']
        running_count = r['runningCount']
        age = humanize.naturaltime(now - created_at)
        row = (service_name, task_def, desired_count,
               running_count, status, age)
        out.append(row)
    headers = ['NAME', 'TASK DEFINITION', 'DESIRED', 'RUNNING',
               'STATUS', 'AGE']
    output = tabulate.tabulate(out, headers=headers, tablefmt='plain')
    click.echo(output)


@get.command(name='container-instance')
@click.option('--cluster')
@click.option('--sort-by')
@click.pass_context
def get_container_instance(ctx, cluster, sort_by):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    records = bw.get_container_instances(cluster=cluster)
    if sort_by:
        records.sort(key=lambda r: jp(r, sort_by))
    out = []
    for r in records:
        status = r['status']
        ec2_instance_id = r['ec2InstanceId']
        container_instance_arn = r['containerInstanceArn']
        instance_id = display.simple_container_instance(container_instance_arn)
        running_count = r['runningTasksCount']
        row = (instance_id, ec2_instance_id, status, running_count)
        out.append(row)
    headers = ['INSTANCE ID', 'EC2 INSTANCE ID', 'STATUS', 'RUNNING COUNT']
    output = tabulate.tabulate(out, headers=headers, tablefmt='plain')
    click.echo(output)


@get.command(name='task')
@click.option('--cluster')
@click.option('--sort-by')
@click.pass_context
def get_task(ctx, cluster, sort_by):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    records = bw.get_tasks(cluster=cluster)
    if sort_by:
        records.sort(key=lambda r: jp(r, sort_by))
    out = []
    now = datetime.datetime.now(pytz.utc)
    for r in records:
        status = r['lastStatus']
        created_at = r['createdAt']
        task_id = display.simple_task(r['taskArn'])
        task_def = display.simple_task_definition(r['taskDefinitionArn'])
        age = humanize.naturaltime(now - created_at)
        row = (task_id, status, task_def, age)
        out.append(row)
    headers = ['TASK ID', 'STATUS', 'TASK DEFINITION', 'AGE']
    output = tabulate.tabulate(out, headers=headers, tablefmt='plain')
    click.echo(output)


@get.command(name='task-definition-family')
@click.option('--family-prefix', default=None)
@click.option('--status', type=click.Choice(TASK_DEFINITION_STATUS),
              default='ACTIVE')
@click.pass_context
def get_task_definition_family(ctx, status, family_prefix):
    bw = ctx.obj['bw']
    records = bw.all_task_definition_families(
        family_prefix=family_prefix,
        status=status,
    )
    for r in records:
        click.echo(r)


@get.command(name='task-definition')
@click.option('--family-prefix', default=None)
@click.option('--status', type=click.Choice(TASK_DEFINITION_STATUS),
              default='ACTIVE')
@click.pass_context
def get_task_definition(ctx, status, family_prefix):
    bw = ctx.obj['bw']
    records = bw.all_task_definitions(
        family_prefix=family_prefix,
        status=status,
    )
    for r in records:
        out = display.simple_task_definition(r)
        click.echo(out)


@cli.command(short_help='Run a particular task definition on the cluster.')
@click.option('--task-definition', required=True)
@click.option('--cluster')
@click.option('--container', default=None)
@click.option('--user', default=None)
@click.option('--ssh-port', default=22, type=int)
@click.argument('command')
@click.pass_context
def run(ctx, task_definition, cluster, command, ssh_port, container, user):
    if not cluster:
        cluster = ctx.obj['cluster']
    if not ssh_port:
        ssh_port = int(ctx.obj['ssh_port'])
    if not user:
        if 'ECS_USER' in os.environ:
            user = os.environ.get('ECS_USER')
        else:
            user = os.environ.get('USER')
    bw = ctx.obj['bw']
    task_arn = bw.run(cluster=cluster, task_definition=task_definition)
    print('Got task ARN. Wait 30 sec for task to start')
    time.sleep(30)
    ssh = Ssh(bw=bw, task=task_arn, command=command, cluster=cluster,
              port=ssh_port, user=user, container=container)
    ssh.exec_command()


@cli.command(short_help='Set a new size for a service')
@click.option('--cluster')
@click.option('--replicas', type=int, required=True)
@click.argument('service', required=True)
@click.pass_context
def scale(ctx, replicas, service, cluster):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    resp = bw.scale_service(service, replicas, cluster=cluster)
    output = resp['service']['serviceArn']
    click.echo(output)


@cli.group(cls=AliasedGroup,
           short_help='Stop service.')
def stop():
    pass


@stop.command(name='task')
@click.option('--cluster')
@click.option('--reason', default='Stopped with ecsctl')
@click.option('--raw-response', default=False, show_default=True)
@click.argument('task', required=True)
@click.pass_context
def stop_task(ctx, task, cluster, reason, raw_response):
    if not cluster:
        cluster = ctx.obj['cluster']
    bw = ctx.obj['bw']
    resp = bw.stop_task(task, cluster=cluster, reason=reason)
    if raw_response:
        click.echo(display.de_unicode(resp['task']))
    else:
        click.echo(resp['task']['taskArn'])
