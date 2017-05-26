
import boto3


class BotoWrapper:

    def __init__(self, session=None):
        if not session:
            session = boto3.session.Session()
        self.session = session
        self.ecs_client = session.client('ecs')
        self.ec2_client = session.client('ec2')

    def describe_instance(self, instance_id):
        resp = self.ec2_client.describe_instances(InstanceIds=[instance_id])
        return resp['Reservations'][0]['Instances'][0]

    def all_service_arns(self, cluster='default'):
        paginator = self.ecs_client.get_paginator('list_services')
        out = []
        for page in paginator.paginate(cluster=cluster):
            out += page['serviceArns']
        return out

    def get_services(self, cluster='default'):
        services = self.all_service_arns(cluster=cluster)
        out = []
        while services:
            batch_services, services = services[:10], services[10:]
            resp = self.ecs_client.describe_services(
                cluster=cluster,
                services=batch_services,
            )
            out += resp['services']
        return out

    def describe_service(self, service, cluster='default'):
        resp = self.ecs_client.describe_services(
            cluster=cluster,
            services=[service],
        )
        if not resp['services']:
            raise Exception('Service not found.')
        return resp['services'][0]

    def all_container_instance_arns(self, cluster='default'):
        paginator = self.ecs_client.get_paginator('list_container_instances')
        out = []
        for page in paginator.paginate(cluster=cluster):
            out += page['containerInstanceArns']
        return out

    def get_container_instances(self, cluster='default'):
        nodes = self.all_container_instance_arns(cluster=cluster)
        out = []
        while nodes:
            batch_nodes, nodes = nodes[:100], nodes[100:]
            resp = self.ecs_client.describe_container_instances(
                cluster=cluster,
                containerInstances=batch_nodes,
            )
            out += resp['containerInstances']
        return out

    def describe_container_instance(self, node, cluster='default'):
        resp = self.ecs_client.describe_container_instances(
            cluster=cluster,
            containerInstances=[node],
        )
        return resp['containerInstances'][0]

    def all_cluster_arns(self):
        resp = self.ecs_client.list_clusters()
        return resp['clusterArns']

    def get_clusters(self):
        clusters = self.all_cluster_arns()
        out = []
        while clusters:
            batch_clusters, clusters = clusters[:10], clusters[10:]
            resp = self.ecs_client.describe_clusters(
                clusters=batch_clusters,
            )
            out += resp['clusters']
        return out


    def describe_cluster(self, cluster):
        resp = self.ecs_client.describe_clusters(
            clusters=[cluster],
        )
        return resp['clusters'][0]

    def create_cluster(self, cluster):
        resp = self.ecs_client.create_cluster(
            clusterName=cluster,
        )
        return resp['cluster']

    def delete_cluster(self, cluster):
        resp = self.ecs_client.delete_cluster(
            cluster=cluster,
        )
        return resp['cluster']

    def delete_service(self, service, cluster='default', force=False):
        if force:
            resp = self.ecs_client.update_service(
                service=service,
                cluster=cluster,
                desiredCount=0,
            )
        resp = self.ecs_client.delete_service(
            service=service,
            cluster=cluster,
        )
        return resp

    def all_tasks(self, cluster='default'):
        paginator = self.ecs_client.get_paginator('list_tasks')
        out = []
        for page in paginator.paginate(cluster=cluster):
            out += page['taskArns']
        return out

    def get_tasks(self, cluster):
        tasks = self.all_tasks(cluster=cluster)
        out = []
        while tasks:
            batch_tasks, tasks = tasks[:100], tasks[100:]
            resp = self.ecs_client.describe_tasks(
                tasks=batch_tasks,
                cluster=cluster,
            )
            out += resp['tasks']
        return out

    def all_task_definition_families(self, family_prefix=None, status='ALL'):
        paginator = self.ecs_client.get_paginator('list_task_definition_families')
        out = []
        params = dict(familyPrefix=family_prefix, status=status)
        for page in paginator.paginate(**params):
            out += page['families']
        return out

    def all_task_definitions(self, family_prefix=None, status='ALL'):
        paginator = self.ecs_client.get_paginator('list_task_definitions')
        out = []
        params = dict(familyPrefix=family_prefix, status=status)
        for page in paginator.paginate(**params):
            out += page['taskDefinitionArns']
        return out

    def describe_task(self, task, cluster='default'):
        resp = self.ecs_client.describe_tasks(
            tasks=[task],
            cluster=cluster,
        )
        if not resp['tasks']:
            raise Exception('Task not found.')
        return resp['tasks'][0]

    def describe_task_definition(self, task_definition, cluster='default'):
        resp = self.ecs_client.describe_task_definition(
            taskDefinition=task_definition,
        )
        return resp['taskDefinition']

    def run(self, name=None, cluster='default', command=(),
            image=None, cpu=1024, memory=2048, count=1):
        task_def_family = name
        container_name = name
        service_name = '%s-svc' % name
        container_definition = {
            'name': container_name,
            'image': image,
            'cpu': cpu,
            'memory': memory,
        }
        if command:
            container_definition['command'] = 'command'
        resp = self.ecs_client.register_task_definition(
            family=task_def_family,
            containerDefinitions=[container_definition],
        )
        task_def_arn = resp['taskDefinition']['taskDefinitionArn']
        resp = self.ecs_client.create_service(
            cluster=cluster,
            serviceName=service_name,
            taskDefinition=task_def_arn,
            desiredCount=count,
        )

    def stop_task(self, task, cluster='default', reason='Stopped with ecsctl.'):
        resp = self.ecs_client.stop_task(task=task, cluster=cluster, reason=reason)
        return resp

    def drain_node(self, node, cluster='default'):
        resp = self.ecs_client.update_container_instances_state(
            cluster=cluster,
            containerInstances=[node],
            status='DRAINING',
        )
        return resp

    def undrain_node(self, node, cluster='default'):
        resp = self.ecs_client.update_container_instances_state(
            cluster=cluster,
            containerInstances=[node],
            status='ACTIVE',
        )
        return resp

    def scale_service(self, service, count, cluster='default'):
        resp = self.ecs_client.update_service(
            cluster=cluster,
            service=service,
            desiredCount=count,
        )
        return resp
