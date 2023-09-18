
from pathlib import Path
from qpandalite.task.originq import *

circuit_1 = \
'''
QINIT 72
CREG 5
RY q[45],(-2.214297435588181)
RY q[46],(-1.570796)
RZ q[46],(-3.141593)
CZ q[45],q[46]
RY q[46],(-1.0471975511965979)
CZ q[45],q[46]
RY q[46],(-2.0943951023931953)
RZ q[46],(-3.141593)
RY q[52],(-1.570796)
RZ q[52],(-3.141593)
CZ q[46],q[52]
RY q[52],(-0.9553166181245093)
CZ q[46],q[52]
RY q[52],(-2.186276035465284)
RZ q[52],(-3.141593)
RY q[53],(-1.570796)
RZ q[53],(-3.141593)
CZ q[52],q[53]
RY q[53],(-0.7853981633974483)
CZ q[52],q[53]
RY q[53],(-2.356194490192345)
RZ q[53],(-3.141593)
CONTROL q[45]
RY q[46],(-2.0943951023931957)
ENDCONTROL
CONTROL q[46]
RY q[52],(-1.9106332362490186)
ENDCONTROL
CONTROL q[52]
RY q[53],(-1.5707963267948966)
ENDCONTROL
CNOT q[53],q[54]
CNOT q[52],q[53]
CNOT q[46],q[52]
CNOT q[45],q[46]
X q[45]
MEASURE q[45], c[0]
MEASURE q[46], c[1]
MEASURE q[52], c[2]
MEASURE q[53], c[3]
MEASURE q[54], c[4]
'''.strip()


def get_token(pilot_api):
    request_body = dict()
    request_body['apiKey'] = pilot_api
    request_body = json.dumps(request_body)
    url = 'https://10.10.7.99:10080/management/pilotosmachinelogin'
    response = requests.post(url=url, data=request_body, verify=False)
    status_code = response.status_code
    if status_code != 200:
        raise RuntimeError(f'Error in query_by_taskid. '
                           'The returned status code is not 200.'
                           f' Response: {response.text}')

    text = response.text
    response = json.loads(text)
    token = response['token']
    try:
        with open('originq_online_config.json', 'r') as fp:
            default_online_config = json.load(fp)
        default_online_config['default_token'] = token
        with open('originq_online_config.json', 'w') as fp:
            json.dump(default_online_config, fp)
    except:
        warnings.warn('originq_online_config.json is not found. '
                      'It should be always placed at current working directory (cwd).')

    return token


if __name__ == '__main__':
    circuit = circuit_1

    token = get_token('035147B99D20486AACAAF5F270B9F161')
    # print(token)
    #
    taskid = submit_task_compile_only(
        circuit,
        circuit_optimize=True,
        auto_mapping=False,
        task_name='CompileOnlyTest',
        savepath = Path.cwd() / 'origin_online_info_verify')
