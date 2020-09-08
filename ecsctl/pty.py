
import docker
import dockerpty


class Pty:
    def __init__(self, bw=None, task=None, command=(),
                 port=2375, stdin=False, tty=False, cluster='default',
                 api_version=None, container=None):
        self.bw = bw
        self.task = task
        self.command = command
        self.port = port
        self.stdin = stdin
        self.tty = tty
        self.cluster = cluster
        self.container = container
        self.api_version = api_version

    def get_ecs_hostname_of_task(self):
        info = self.bw.describe_task(self.task, cluster=self.cluster)
        ecs_containers = info['containers']
        ecs_containers_id = ecs_containers[0]['runtimeId']
        first_container_name = ecs_containers[0]['name']
        if info['launchType'] == 'FARGATE':
            raise Exception('"exec" does not work with FARGATE.')
        container_instance = info['containerInstanceArn']
        node_info = self.bw.describe_container_instance(
            container_instance,
            cluster=self.cluster,
        )
        ec2_instance_id = node_info['ec2InstanceId']
        ec2_info = self.bw.describe_instance(ec2_instance_id)
        return first_container_name, ec2_info['PrivateIpAddress'], ecs_containers_id

    def find_container_id(self, client, container_name):
        containers = client.containers()
        for container in containers:
            labels = container.get('Labels')
            if not labels:
                continue
            name = labels.get('com.amazonaws.ecs.container-name')
            if name == container_name:
                return container['Id']
        else:
            raise Exception('container not found.')

    def exec_command(self):
        first_container_name, hostname, container_id = self.get_ecs_hostname_of_task()
        docker_url = '%s:%d' % (hostname, self.port)
        client = docker.APIClient(
            docker_url,
            version=self.api_version,
        )
        if self.container is not None:
            container = self.container
            container_id = self.find_container_id(client, container)
        resp = client.exec_create(
            container_id, self.command, stdin=self.stdin, tty=self.tty
        )
        exec_id = resp['Id']
        dockerpty.start_exec(client, exec_id, interactive=self.stdin)
