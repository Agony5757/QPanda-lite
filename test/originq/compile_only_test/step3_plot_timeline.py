import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path
from qpandalite.task.originq import *
import qpandalite
from .step1_submit_circuit import savepath

figure_save_path = Path.cwd() / 'timeline_plot'

if __name__ == '__main__':
    online_info = load_all_online_info(savepath=savepath)
    query_all_task(savepath=savepath)

    transformed_prog = []
    time_line_table_list = []
    not_finished = []

    for task in online_info:
        taskid = task['taskid']
        taskname = '' if 'taskname' not in task else task['taskname']
        if not os.path.exists(savepath / f'{taskid}.txt'):
            not_finished.append({'taskid': taskid, 'taskname': taskname})

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

            compiled_prog = taskinfo["timeline"][0]
            qpandalite.plot_time_line(compiled_prog, taskid, 
                           figure_save_path=figure_save_path)
            # new_prog, qubit_list, time_line = format_result(compiled_prog)
            # transformed_prog.append(new_prog)
            # time_line_table_list.append(create_time_line_table(new_prog, qubit_list, time_line))

