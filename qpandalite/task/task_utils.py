import requests
from pathlib import Path
import os
import json

def load_circuit(basepath = None):
    circuits = dict()
    if not basepath:
        basepath = Path.cwd() / 'output_circuits'

    files = os.listdir(basepath)    
    
    for file in files:
        if file.endswith('txt'):
            with open(basepath / file, 'r') as fp:
                circuit_text = fp.read()
            circuits[file] = circuit_text

    return circuits

def load_circuit_group(path = None):
    circuits = dict()
    if not path:
        path = Path.cwd() / 'output_circuits' / 'originir.txt'

    with open(path, 'r') as fp:
        circuit_text = fp.read()

    originirs = circuit_text.split('//////////')
    for i, originir in enumerate(originirs):
        stripped = originir.strip()
        if stripped and stripped.startswith('QINIT'):
            circuits[i] = stripped

    return circuits

def make_savepath(savepath = None):    
    if not savepath:
        savepath = Path.cwd() / 'online_info'

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    if not os.path.exists(savepath / 'online_info.txt'):
        with open(savepath / 'online_info.txt', 'w') as fp:
            pass

def load_all_online_info(savepath = None): 
    if not savepath:
        savepath = Path.cwd() / 'online_info'
    online_info = []
    with open(savepath / 'online_info.txt', 'r') as fp:
        lines = fp.read().strip().splitlines()

        for line in lines:
            online_info.append(json.loads(line))

    return online_info       

def write_taskinfo(taskid, taskinfo, savepath = None):
    if not savepath:
        savepath = Path.cwd() / 'online_info'
    with open(savepath / '{}.txt'.format(taskid), 'w') as fp:
        json.dump(taskinfo, fp)