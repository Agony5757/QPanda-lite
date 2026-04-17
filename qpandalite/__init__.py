from pathlib import Path

from . import config
from .circuit_builder import Circuit
from .originir import OriginIR_BaseParser
from .qasm import OpenQASM2_BaseParser
try:
    from .simulator import OriginIR_Simulator
except:
    # warning has been omitted in the submodule.
    pass
try:
    import qpandalite_cpp
except ImportError:
    import warnings
    warnings.warn('qpandalite is not installed with QPandaLiteCpp.')
from .analyzer import convert_originq_result, convert_quafu_result, calculate_expectation, shots2prob, kv2list
from .qcloud_config.originq_online_config import (create_originq_online_config,
                                                  create_originq_dummy_config,
                                                  create_originq_config)
from .qcloud_config.quafu_online_config import create_quafu_online_config
from .qcloud_config.ibm_online_config import create_ibm_online_config
from .qcloud_config.originq_cloud_config import create_originq_cloud_config

# Optional import - requires visualization dependencies (pandas, matplotlib)
try:
    from .transpiler import plot_time_line
except ImportError:
    pass

from .task.task_utils import (get_last_taskid, load_circuit, load_circuit_group, load_all_online_info)

from .circuit_adapter import (
    CircuitAdapter,
    OriginQCircuitAdapter,
    QuafuCircuitAdapter,
    IBMCircuitAdapter,
)

from .exceptions import (
    QPandaLiteError,
    AuthenticationError,
    InsufficientCreditsError,
    QuotaExceededError,
    NetworkError,
    TaskFailedError,
    TaskTimeoutError,
    TaskNotFoundError,
    BackendError,
    BackendNotAvailableError,
    BackendNotFoundError,
    CircuitError,
    CircuitTranslationError,
    UnsupportedGateError,
)

from .task_manager import (
    submit_task,
    submit_batch,
    query_task,
    wait_for_result,
    save_task,
    get_task,
    list_tasks,
    clear_completed_tasks,
    clear_cache,
    TaskInfo,
    TaskManager,
)

from .network_utils import (
    check_proxy_connectivity,
    detect_system_proxy,
    test_ibm_connectivity,
    get_ibm_proxy_from_config,
)

from .version import __version__