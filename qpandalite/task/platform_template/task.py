'''A summary for all interfaces provided by QPanda-lite across platforms.

   submit_task
   query_by_taskid
   query_by_taskid_sync
   query_all_tasks
'''

from typing import Any, Union, List, AnyStr
from os import PathLike

def submit_task(
    circuit : Union[List[str], str], 
    task_name : str, 
    tasktype : Any,
    chip_id : Any,
    shots : int,
    circuit_optimize : Union[bool, Any],
    measurement_amend : Union[bool, Any],
    auto_mapping : Union[bool, Any],
    specified_block : Union[bool, Any],
    savepath : PathLike,
    url : Union[str, Any],
    **kwargs
):   
    pass

def query_by_taskid(taskid : Union[List[str], str], 
                    url : Union[str, Any], 
                    **kwargs
                    ):
    pass

def query_by_taskid_sync(taskid : Union[List[str], str], 
                         interval : float, 
                         timeout : float, 
                         retry : int,
                         url : Union[str, Any],
                         **kwargs):
    pass


def query_all_task(url : Union[str, Any], 
                   savepath : Union[str, Any],
                   **kwargs):
    pass
    