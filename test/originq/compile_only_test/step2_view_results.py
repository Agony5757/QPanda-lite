import json
import os
from pathlib import Path
from qpandalite.task.originq import *
from step1_submit_circuit import savepath

if __name__ == '__main__':

    online_info = load_all_online_info(savepath = savepath)
    query_all_task(savepath = savepath)

    not_finished = []

    for task in online_info:
        taskid = task['taskid']
        taskname = '' if 'taskname' not in task else task['taskname']
        if not os.path.exists(savepath / f'{taskid}.txt'):
            not_finished.append({'taskid':taskid, 'taskname':taskname})

    if not_finished:
        print('Unfinished task list')
        for task in not_finished:
            taskid = task['taskid']
            taskname = task['taskname'] if task['taskname'] else 'null'
            print(f'  taskid:{taskid}, taskname:{taskname}')
        print(f'Unfinished: {len(not_finished)}')
    else:
        for task in online_info:
            taskid = task['taskid']
            print(f'Taskid: {taskid}')
            with open(savepath / f'{taskid}.txt') as fp:            
                taskinfo = json.load(fp)

            if taskinfo['status'] == 'failed':
                continue
            
            compiled_prog = taskinfo["compiled_prog"]
            print(compiled_prog[0])
            

            