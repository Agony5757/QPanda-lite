'''This is the demo for QPanda-lite

# 2. Run in the dummy server

## Concepts:
    
    Result adapter: QPanda-lite helps you to adapt the result to a platform-independent type.

    KeyValue style: Result in key-value style is like: {'0000':0.1, '0001': 0.2, ...}
    List style: Result in list style is like [0.1, 0.2, ...]  
    Prob style: Return in [0.1, 0.2, ...], sum to 1.0
    Shots style: Return in [1000, 2000, ...], sum to 'shots'

    Reverse key: The platform may have different endians (big-endian or small-endian). Reverse-key is to change between them.

'''

import qpandalite
import qpandalite.task.originq_dummy as originq
import math

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

if __name__ == '__main__':

    mapping = {0 : 10, 1: 11, 2: 12, 3: 13}
    circuit = build_circuit(mapping)
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

