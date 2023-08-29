from qpandalite import create_originq_online_config

if __name__ == '__main__':

    # The originq qpilot login state token
    token = 'DAD349A30FCC4748'

    # The url for submitting the task
    submit_url = 'https://10.10.7.99:10080/task/realQuantum/run'

    # The url for querying the task     
    query_url = 'http://10.10.7.99:5000/test-api//management/query/taskinfo'
    
    # The maximum task group size, representing the maximum number of 
    # quantum circuits contained in a single task. (default = 200)
    task_group_size = 200

    create_originq_online_config(default_token = token, 
                                 default_submit_url = submit_url, 
                                 default_query_url = query_url, 
                                 default_task_group_size = task_group_size)