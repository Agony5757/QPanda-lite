"""Utility functions for quantum task management.

Provides helpers for loading/saving circuit files, managing local task
records (``online_info``), and generating timestamp strings.  These are
used internally by the platform-specific task modules.
"""

import requests
from pathlib import Path
import os
import json
from datetime import datetime

def load_circuit(basepath = None):
    '''Load all quantum circuits from text files under *basepath*.

    Each ``.txt`` file is read as a single circuit string and stored in a
    dict keyed by filename.

    Args:
        basepath (os.PathLike, optional): Directory containing circuit files.
            Defaults to ``<cwd>/output_circuits``.

    Returns:
        dict[str, str]: Mapping from filename to circuit text.
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
    '''Load multiple circuits from a single grouped circuit file.

    The file is split on the ``//////////`` delimiter.  Only non-empty
    fragments starting with ``QINIT`` are kept.

    Args:
        path (os.PathLike, optional): Path to the grouped circuit file.
            Defaults to ``<cwd>/output_circuits/originir.txt``.

    Returns:
        dict[int, str]: Mapping from index to circuit text.
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
    '''Ensure the save directory and ``online_info.txt`` exist.

    Creates *savepath* and an empty ``online_info.txt`` inside it if they
    do not already exist.

    Args:
        savepath (os.PathLike, optional): Target directory.
            Defaults to ``<cwd>/online_info``.
    '''
    if not savepath:
        savepath = Path.cwd() / 'online_info'

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    if not os.path.exists(savepath / 'online_info.txt'):
        with open(savepath / 'online_info.txt', 'w') as fp:
            pass

def load_all_online_info(savepath = None): 
    '''Load all locally saved online task info entries.

    Reads ``online_info.txt`` line-by-line; each line is expected to be a
    JSON object.

    Args:
        savepath (os.PathLike, optional): Directory containing
            ``online_info.txt``.  Defaults to ``<cwd>/online_info``.

    Returns:
        list[dict]: A list of parsed JSON objects.
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
    '''Return the task ID of the most recently submitted task.

    Args:
        savepath (os.PathLike, optional): Directory containing
            ``online_info.txt``.  Defaults to ``<cwd>/online_info``.

    Returns:
        str: The taskid from the last line of ``online_info.txt``.
    '''
    if not savepath:
        savepath = Path.cwd() / 'online_info'

    with open(savepath / 'online_info.txt', 'r') as fp:
        lines = fp.read().strip().splitlines()
        last_task = json.loads(lines[-1])
    
    return last_task['taskid']


def write_taskinfo(taskid, taskinfo, savepath = None):
    '''Persist task info to a per-task JSON file.

    Writes ``<savepath>/<taskid>.txt`` containing the JSON-serialized
    *taskinfo*.  If *savepath* is ``None``, nothing is written.  Existing
    files are never overwritten.

    Args:
        taskid (str): The task ID used as the filename.
        taskinfo (dict): Task information to save.
        savepath (os.PathLike, optional): Target directory.  If ``None``,
            the call is a no-op.
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
    """Return a human-readable timestamp string (``YYYYMMDD_HHMMSS``)."""
    return timestr_ymd_hms()

def timestr_ymd_hms():
    """Return the current time formatted as ``YYYYMMDD_HHMMSS``."""
    return datetime.now().strftime(r"%Y%m%d_%H%M%S")
    