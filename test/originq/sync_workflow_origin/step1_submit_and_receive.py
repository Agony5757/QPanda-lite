import time
import qpandalite.task.originq as origin

q1 = 52
q2 = 53

circuit_template = '''
QINIT 72
CREG 2
RY {q1}, ({{theta1}})
RY {q2}, ({{theta2}})
CZ {q1},{q2}
RY {q1}, ({{theta3}})
RY {q2}, ({{theta4}})
MEASURE {q1}, c[0]
MEASURE {q2}, c[1]
'''.format(q1='q[{}]'.format(q1), q2='q[{}]'.format(q2))

theta1 = 0.5
theta2 = 0.5
theta3 = 0.5
theta4 = 0.5

circuit = circuit_template.format(theta1 = theta1,
                        theta2 = theta2,
                        theta3 = theta3,
                        theta4 = theta4)

# create circuit
circuit = circuit.strip()

t1 = time.time()

# submit task
taskid = origin.submit_task_group([circuit], savepath=None)
print(f'Taskid={taskid}')

# fetch result synchronously
result = origin.query_by_taskid_sync(taskid)    
print('Success!')
print(result)

# see duration time
t2 = time.time()
print(f'Duration = {t2-t1} sec')