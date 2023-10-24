from qpandalite import (create_originq_online_config,
                        create_originq_dummy_config,
                        create_originq_config)

if __name__ == '__main__':

    # The originq qpilot login apitoken
    apitoken = 'TOKEN'

    # The url for logging
    login_url = 'LOGIN_URL'

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

    # see also create_originq_online_config and create_originq_dummy_config
    create_originq_config(login_apitoken = apitoken, 
                          login_url = login_url,
                          submit_url = submit_url, 
                          query_url = query_url, 
                          available_qubits = available_qubits,
                          available_topology = available_topology,
                          task_group_size = task_group_size)
