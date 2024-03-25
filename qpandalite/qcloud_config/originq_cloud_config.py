import json
from pathlib import Path


def create_originq_cloud_config(apitoken=None,
                          submit_url=None,
                          query_url=None,
                          available_qubits=None,
                          available_topology=None,
                          task_group_size=200,
                          savepath = None):
    if not apitoken:
        raise RuntimeError('You should input your api key.')

    if not submit_url:
        raise RuntimeError('You should input the submitting url (url 1).')

    if not query_url:
        raise RuntimeError('You should input the querying url (url 2).')

    if not isinstance(available_qubits, list):
        raise RuntimeError('Available qubits must be a list.')

    if not isinstance(available_topology, list):
        raise RuntimeError('Available topology must be a list.')

    if not isinstance(task_group_size, int):
        raise RuntimeError('Task group size (task_group_size) must be a number.')
    
    if not savepath:
        savepath = Path.cwd()

    default_online_config = {
        'apitoken': apitoken,
        'submit_url': submit_url,
        'query_url': query_url,
        'available_qubits': available_qubits,
        'available_topology': available_topology,
        'task_group_size': task_group_size,
    }

    with open(savepath / 'originq_cloud_config.json', 'w') as fp:
        json.dump(default_online_config, fp, indent=2)


def create_originq_online_cloud_config(apitoken=None,
                                 submit_url=None,
                                 query_url=None,
                                 task_group_size=200,
                                 savepath = None):
    if not apitoken:
        raise RuntimeError('You should input your api key.')

    if not submit_url:
        raise RuntimeError('You should input the submitting url (url 1).')

    if not query_url:
        raise RuntimeError('You should input the querying url (url 2).')

    if not isinstance(task_group_size, int):
        raise RuntimeError('Task group size (task_group_size) must be a number.')
    
    if not savepath:
        savepath = Path.cwd()

    default_online_config = {
        'apitoken': apitoken,
        'submit_url': submit_url,
        'query_url': query_url,
        'available_qubits': None,
        'available_topology': None,
        'task_group_size': task_group_size,
    }

    with open(savepath / 'originq_cloud_config.json', 'w') as fp:
        json.dump(default_online_config, fp, indent=2)


if __name__ == '__main__':
    # The originq qpilot login apitoken
    apitoken = 'TOKEN'

    # The url for submitting the task
    submit_url = 'SUBMIT_URL'

    # The url for querying the task
    query_url = 'QUERY_URL'

    # Available qubits
    available_qubits = [0, 1, 2]

    # Available topology
    available_topology = [[0, 1], [1, 2]]

    # The maximum task group size, representing the maximum number of
    # quantum circuits contained in a single task. (default = 200)
    task_group_size = 200

    create_originq_cloud_config(apitoken=apitoken,
                                 submit_url=submit_url,
                                 query_url=query_url,
                                 available_qubits=available_qubits,
                                 available_topology=available_topology,
                                 task_group_size=task_group_size)
