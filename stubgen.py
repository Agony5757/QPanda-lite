# check if pybind11-stubgen is installed
try:
    import pybind11_stubgen
except ImportError:
    print("pybind11-stubgen is not installed, please install it by running 'pip install pybind11-stubgen'")
    exit()

import subprocess
# generate stub for QPandaLitePy on the package directory
# execute : pybind11-stubgen QPandaLitePy -o qpandalite
subprocess.run(["pybind11-stubgen", "QPandaLitePy", "-o", "qpandalite/simulator"])