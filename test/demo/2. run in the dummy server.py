'''This is the demo for QPanda-lite

# 2. Run in the dummy server

## Concepts:
    
    Dummy server: a fake server that produces a locally simulated result instead really sending them to the server. This is used to test your program before real task submission.

## About importing different platforms, OriginQ, Quafu, IBM and their 'dummies'

    QPanda-lite is prepared for a more convenient migration from 'dummy' to 'real chip', even from 'originq' to 'ibm' or 'quafu'.

    All task submission and result fetching methods are:
        - submit_task
        - query_by_taskid
        - query_all_tasks

    Migrating from one platform to another is like:

        Example A:

        if use_dummy:
            import qpandalite.task.originq_dummy as originq
        else:
            import qpandalite.task.originq as originq

        Example B:
            
        if platform == 'originq':
            import qpandalite.task.originq as task
        elif platform == 'ibm':
            import qpandalite.task.ibm as task
        elif platform == 'quafu':
            import qpandalite.task.quafu as task

    Then you can use task.submit_task and other functions to write compatible codes for all platforms.

## Compatibility

    QPanda-lite tries to keep the arguments for those functions being the same across all platforms. However, some arguments are not compatible now, and will be repaired over time.

    QPanda-lite also gaurantees that 'dummy' server has the very same returns as the 'real' server.

## Task group

    QPanda-lite always assumes you inputting a 'List[str]' to submit_task. If you only input one circuit, it automatically changes your input to a list. As the result, the return of query_by_taskid is also a 'List'.

    task_group_size is a parameter that indicates how many number of circuits can be bound in a single taskid. If you have thousands of circuits that may bind to an unknown number of tasks? Don't worry. QPanda-lite helps you binding them and always returning them as if they are worked together. If you input 5000 circuits to submit_task, it will generate 5000 taskids if sending to Quafu, and return a 5000-sized list of results with query_by_taskid.

'''

import qpandalite
import math

def build_circuit(mapping):    
    c = qpandalite.Circuit()

    c.x(0)
    c.rx(1, math.pi)
    c.ry(2, math.pi / 2)
    c.cnot(2, 3)
    c.cz(1, 2)
    c.measure(0,1,2)
    c = c.remapping(mapping)
    return c.circuit

def demo_2():
    # Note that this 'create config' only needs to be executed once. You will see your originq_online_config.json in your current working directory.
    qpandalite.create_originq_dummy_config(
        available_qubits=[10, 11, 12, 13],
        available_topology=[[10,11],[11,12],[12,13]], 
        task_group_size=200
    )
    
    # Once you have originq_online_config.json in your current working directory, then import this.
    import qpandalite.task.originq_dummy as originq
    
    # ready for mapping the circuit
    mapping = {0 : 10, 1: 11, 2: 12, 3: 13}

    # create the circuit
    circuit = build_circuit(mapping)

    # submit task will generate a 'taskid'    
    taskid = originq.submit_task(circuit, shots = 1000, task_name='some test')

    # a synchronous mode for query task
    result = originq.query_by_taskid_sync(taskid, 
                                          interval=2.0, # query interval (seconds)
                                          timeout=60.0, # max timeout (seconds)
                                          retry=5 # max retries for exceptions
                                          )
    print(result)
    # Note: the result is ALWAYS a list even if you only input one circuit. QPanda-lite automatically helps you managing a bunch of circuits which may correpond to different number of taskid(s).

    task_status_and_result = originq.query_by_taskid(taskid)
    print(task_status_and_result)
    # returns like (if success):
    # [{
    #   'taskid': '...', 
    #   'taskname': '...', 
    #   'status': 'success', 
    #   'result': [{'key': [...], 'value': [...]}]
    # }]
    # or (if not finished):
    # [{
    #   'taskid': '...', 
    #   'taskname': '...', 
    #   'status': 'running', 
    # }]
    # or (if failed):
    # [{
    #   'taskid': '...', 
    #   'taskname': '...', 
    #   'status': 'failed', 
    # }]

    if task_status_and_result['status'] == 'success':
        result = task_status_and_result['result']
        print(result)


if __name__ == '__main__':
    demo_2()