import uuid
from datetime import datetime


class Services:
    def __init__(self):
        self._service_list = []

    def register(self, type, ipaddr, port):
        service_uuid = str(uuid.uuid4())
        new_service = {
            'uuid': service_uuid,
            'type': type,
            'ip': ipaddr,
            'port': port,
            'heartbeat': datetime.now()
        }
        self._service_list.append(new_service)
        return service_uuid

    def heartbeat(self, service_uuid):
        for service in self._service_list:
            if service['uuid'] == service_uuid:
                service['heartbeat'] = datetime.now()
                return 'OK'
        return 'NOT FOUND'

    def query(self, type):
        results = []
        for index, service in enumerate(self._service_list):
            age = (datetime.now() - service['heartbeat']).total_seconds()
            if age > 5:
                self._service_list.pop(index)
            elif service['type'] == type:
                results.append(
                    {
                        'ip': service['ip'],
                        'port': service['port']
                    }
                )
        return str(results)