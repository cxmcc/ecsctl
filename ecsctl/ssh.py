from shell_command import shell_call

class Ssh:
    def __init__(self, bw=None, task=None, command=None,
                 port=22, cluster='default',
                 user=None, container=None):
        self.bw = bw
        self.task = task
        self.command = command
        self.port = port
        self.cluster = cluster
        self.container = container
        self.user = user

    def get_ecs_hostname_of_task(self):
        info = self.bw.describe_task(self.task, cluster=self.cluster)
        ecs_containers = info['containers']
        first_container_name = ecs_containers[0]['name']
        container_instance = info['containerInstanceArn']
        node_info = self.bw.describe_container_instance(
            container_instance,
            cluster=self.cluster,
        )
        ec2_instance_id = node_info['ec2InstanceId']
        ec2_info = self.bw.describe_instance(ec2_instance_id)
        return first_container_name, ec2_info['PrivateIpAddress']

    def filter_string(self,container):
        return '--filter "label=com.amazonaws.ecs.container-name=%s"' % (container)

    def exec_command(self):
        first_container_name, hostname = self.get_ecs_hostname_of_task()
        if self.container is None:
            container = first_container_name
        else:
            container = self.container
        ssh = 'ssh -tt -p %d %s@%s sudo docker exec -it \$\(sudo docker ps -q %s\) %s' % (self.port, self.user,
                hostname, self.filter_string(container), self.command)
        #print ssh
        shell_call(ssh)
