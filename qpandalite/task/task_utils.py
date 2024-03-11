import requests
from pathlib import Path
import os
import json
from datetime import datetime

def load_circuit(basepath = None):
    '''Load all quantum circuits under the basepath.

    Args:
        basepath (PathLikeObject(str, pathlib.Path, etc...), optional): The path to the circuits. Defaults to None.

    Returns:
        List[str]: The loaded quantum circuits.
    '''
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
    '''Load circuit group from the grouped circuit file.

    Args:
        path (PathLikeObject(str, pathlib.Path, etc...), optional): The path to the circuit file. Defaults to None.

    Returns:
        List[str]: The loaded quantum circuits.
    '''
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
    '''Make the savepath

    Args:
        savepath (PathLikeObject(str, pathlib.Path, etc...), optional): The savepath. Defaults to None.
    '''
    if not savepath:
        savepath = Path.cwd() / 'online_info'

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    if not os.path.exists(savepath / 'online_info.txt'):
        with open(savepath / 'online_info.txt', 'w') as fp:
            pass

def load_all_online_info(savepath = None): 
    '''Load all online info under the savepath

    Args:
        savepath (PathLikeObject(str, pathlib.Path, etc...), optional): The savepath. Defaults to Path.cwd() / 'online_info'.

    Returns:
        List[Dict]: A list of online infos
    '''
    if not savepath:
        savepath = Path.cwd() / 'online_info'
    online_info = []
    with open(savepath / 'online_info.txt', 'r') as fp:
        lines = fp.read().strip().splitlines()

        for line in lines:
            online_info.append(json.loads(line))

    return online_info       

def get_last_taskid(savepath = None):
    '''Load the last taskid under the savepath

    Args:
        savepath (PathLikeObject(str, pathlib.Path, etc...), optional): The savepath. Defaults to Path.cwd() / 'online_info'.
    '''
    if not savepath:
        savepath = Path.cwd() / 'online_info'

    with open(savepath / 'online_info.txt', 'r') as fp:
        lines = fp.read().strip().splitlines()
        last_task = json.loads(lines[-1])
    
    return last_task['taskid']


def write_taskinfo(taskid, taskinfo, savepath = None):
    '''Write the task into the online info.

    Args:
        taskid (int): The taskid
        taskinfo (Dict): The taskinfo needed to be saved correponding to the taskid (as a single file)
        savepath (PathLikeObject(str, pathlib.Path, etc...), optional): The savepath. Defaults to None.
    '''

    # if no savepath, then it will not save anything
    if not savepath:
        return
        # savepath = Path.cwd() / 'online_info'

    # no overwrite
    if os.path.exists(savepath / '{}.txt'.format(taskid)):
        return
    
    with open(savepath / '{}.txt'.format(taskid), 'w') as fp:
        json.dump(taskinfo, fp)

def timestr():
    return timestr_ymd_hms()

def timestr_ymd_hms():
    return datetime.now().strftime(r"%Y%m%d_%H%M%S")
    