
import json
from datetime import datetime

def json_serial(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError

def simple_task_definition(arn):
    return arn.partition(':task-definition/')[-1]

def simple_container_instance(arn):
    return arn.partition(':container-instance/')[-1]

def simple_task(arn):
    return arn.partition(':task/')[-1]

def de_unicode(content):
    return json.dumps(content, indent=4, default=json_serial)
