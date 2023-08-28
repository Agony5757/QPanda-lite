import json
from pathlib import Path

if __name__ == '__main__':

    default_token = None
    # default_token = ' INPUT YOUR TOKEN HERE '
    if not default_token:
        raise RuntimeError('You should input your token here.')

    default_submit_url = None
    # default_submit_url = ' INPUT YOUR URL 1 HERE '
    if not default_submit_url:
        raise RuntimeError('You should input the submitting url (url 1) here.')
    
    default_query_url = None
    # default_query_url = ' INPUT YOUR URL 2 HERE '
    if not default_query_url:
        raise RuntimeError('You should input the querying url (url 2) here.')

    default_task_group_size = 200

    default_online_config = {
        'default_token' : default_token,
        'default_submit_url' : default_submit_url,
        'default_query_url': default_query_url,
        'default_task_group_size': default_task_group_size,
    }

    with open(Path.cwd() / 'originq_online_config.json', 'w') as fp:
        json.dump(default_online_config, fp)