
import click

class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        mapping = {
            'svc': 'service',
            'services': 'service',
            'node': 'container-instance',
            'nodes': 'container-instance',
            'container-instances': 'container-instance',
            'clusters': 'cluster',
            'task-definitions': 'task-definition',
            'taskdef': 'task-definition',
            'taskdefs': 'task-definition',
            'task-definition-families': 'task-definition-family',
            'taskdef-family': 'task-definition-family',
            'taskdef-families': 'task-definition-family',
            'tasks': 'task',
        }
        if cmd_name in mapping:
            rv = click.Group.get_command(self, ctx, mapping[cmd_name])
            if rv is not None:
                return rv

