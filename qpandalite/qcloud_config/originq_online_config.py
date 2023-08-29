import json
from pathlib import Path

def create_originq_online_config(default_token = None, 
                                 default_submit_url = None, 
                                 default_query_url = None, 
                                 default_task_group_size = 200):    

    if not default_token:
        raise RuntimeError('You should input your token.')

    if not default_submit_url:
        raise RuntimeError('You should input the submitting url (url 1).')
    
    if not default_query_url:
        raise RuntimeError('You should input the querying url (url 2).')

    if not isinstance(default_task_group_size):
        raise RuntimeError('Task group size (default_task_group_size) must be a number.')

    default_online_config = {
        'default_token' : default_token,
        'default_submit_url' : default_submit_url,
        'default_query_url': default_query_url,
        'default_task_group_size': default_task_group_size,
    }

    with open(Path.cwd() / 'originq_online_config.json', 'w') as fp:
        json.dump(default_online_config, fp)

if __name__ == '__main__':

    # The originq qpilot login state token
    token = ''

    # The url for submitting the task
    submit_url = ''

    # The url for querying the task     
    query_url = ''
    
    # The maximum task group size, representing the maximum number of 
    # quantum circuits contained in a single task. (default = 200)
    task_group_size = 200

    create_originq_online_config(default_token = token, 
                                 default_submit_url = submit_url, 
                                 default_query_url = query_url, 
                                 task_group_size = task_group_size)