import qpandalite
import qpandalite.task.originq_dummy as originq
import math

from qpandalite.test._utils import qpandalite_test

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

def demo_3():
    def build_circuit(mapping):    
        c = qpandalite.Circuit()

        c.x(0)
        c.rx(1, math.pi)
        c.ry(2, math.pi / 2)
        c.cnot(2, 3)
        c.cz(1,2)
        c.measure(0,1,2)
        c = c.remapping(mapping)
        return c.circuit

    #mapping = {0 : 10, 1: 11, 2: 12, 3: 13}
    mapping = {0 : 10, 1: 11, 2: 12, 3: 13}
    circuit = build_circuit(mapping)
    print(circuit)
    taskid = originq.submit_task(circuit, shots = 1000, task_name='some test')
    results = originq.query_by_taskid_sync(taskid, 
                                          interval=2.0, # query interval (seconds)
                                          timeout=60.0, # max timeout (seconds)
                                          retry=5 # max retries for exceptions
                                          )
    print(results)

    # convert to keyvalue-prob style
    results = qpandalite.convert_originq_result(results, 
                                               style = 'keyvalue',
                                               prob_or_shots= 'prob')
    
    print(results)

    # Calculate the expectation
    # Note that the input of calculate_expectation is SAME AS the output of convert_originq_result
    # Every Hamiltonian string has the sequence: '(0)(1)(2)' which is consistent with how the circuit writes.
    exps = [qpandalite.calculate_expectation(result, ['ZII', 'IIZ'])
            for result in results]
    print(exps)

@qpandalite_test('Test Demos')
def run_test_demos():
    demo_2()
    demo_3()

if __name__ == '__main__':
    run_test_demos()