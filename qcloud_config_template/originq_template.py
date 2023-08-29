from qpandalite import create_originq_online_config

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
                                 default_task_group_size = task_group_size)
