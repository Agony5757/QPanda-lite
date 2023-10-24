import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path

def format_result(compiled_prog):
    prog = json.loads(compiled_prog)
    layer_time = {}
    gate_layers = {}
    layer_count = 0
    qubit_list = []
    time_line = []

    for gate in prog:
        gate_name = list(gate.keys())[0]
        gate_parameter = gate[gate_name]

        if gate_name == 'RPhi' and gate_parameter[2] == 90.0:
            gate_name = 'RPhi90'
            qubit = gate_parameter[0]
            angle = gate_parameter[1]
            use_time = gate_parameter[3]
            qubit_list.append(qubit)
        elif gate_name == 'RPhi' and gate_parameter[2] == 180.0:
            gate_name = 'RPhi180'
            qubit = gate_parameter[0]
            angle = gate_parameter[1]
            use_time = gate_parameter[3]
            qubit_list.append(qubit)
        elif gate_name == 'CZ':
            qubit = [gate_parameter[0], gate_parameter[1]]
            angle = 0
            use_time = gate_parameter[2]
            qubit_list.extend(qubit)
        elif gate_name == 'Measure':
            qubit = gate_parameter[0]
            angle = 0
            use_time = gate_parameter[1]
            qubit_list.extend(qubit)
        else:
            qubit = gate_parameter[0]
            angle = 0
            use_time = gate_parameter[-1]
            print('something wrong', gate,  qubit)
            qubit_list.append(qubit)

        if use_time not in layer_time:
            layer_time[use_time] = layer_count
            layer_count += 1
        layer_of_gate = layer_time[use_time]
        if layer_of_gate not in gate_layers:
            gate_layers[layer_of_gate] = []
        gate_layers[layer_of_gate].append((gate_name, qubit, angle, use_time))
        time_line.append(use_time)
        
    return gate_layers, sorted(list(set(qubit_list))), sorted(list(set(time_line)))


def create_time_line_table(layer_dict, qubit_list, time_line):
    time_line_table = pd.DataFrame(columns=time_line, index=['qubit ' + str(i) for i in qubit_list])

    for layer, gates in layer_dict.items():
        for gate_name, qubit, angle, time in gates:
            angle = round(angle, 3)
            if isinstance(qubit, int):
                qubit_name = 'qubit '+str(qubit)
                time_line_table.loc[qubit_name][time] = gate_name + ' ' + str(angle)
            else:
                for q in qubit:
                    qubit_name = 'qubit '+str(q)
                    time_line_table.loc[qubit_name][time] = gate_name + ' ' + str(angle)
    time_line_table = time_line_table.fillna('idle')
    return time_line_table


def plot_time_line(compiled_prog, taskid, 
                   figure_save_path = Path.cwd() / 'timeline_plot'):
    format_prog, qubit_list, time_line = format_result(compiled_prog)
    time_line_table = create_time_line_table(format_prog, qubit_list, time_line)
    depth = len(time_line)
    split_table = depth // 20 + 1
    width = min(20, depth)
    for i in range(1, split_table + 1):
        plt.figure(figsize=(width, len(qubit_list)/2))
        plt.axis('off')
        cmap = {'RPhi90': 'blue', 'RPhi180': 'orange', 'CZ': 'red', 'idle': 'white', 'Measure': 'gray'}

        if i*20 < depth:
            values = time_line_table.values[:, (i-1)*20:i*20]
            columns = time_line_table.columns[(i-1)*20:i*20]
        else:
            values = time_line_table.values[:, (i-1)*20:]
            columns = time_line_table.columns[(i-1)*20:]
        cellColours = [[cmap[x.split(' ')[0]] for x in row] for row in values]
        table = plt.table(cellText=values, colLabels=columns,
                          rowLabels=time_line_table.index,
                          loc='center',
                          cellColours=cellColours)
        
        if not os.path.exists(figure_save_path):
            os.mkdir(figure_save_path)
        plt.savefig(figure_save_path / f'{taskid} timeline {i}.png')

