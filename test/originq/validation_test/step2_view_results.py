import qpandalite.task.originq as originq
import numpy as np
import qpandalite
from step1_submit_circuit import savepath

taskid = qpandalite.get_last_taskid(savepath = savepath)
result = originq.query_by_taskid(taskid)

if result['status'] != 'success':
    print(f'Status: {result["status"]}')
    if result['status'] == 'failed':
        print('Error info: ', result['result'])
    exit(0)

result_list = result['result']

import matplotlib.pyplot as plt
num_subplots = len(result_list)
row = int(np.ceil(num_subplots/3))
fig, axs = plt.subplots(row, 3)

for i, result in enumerate(result_list):
    result_dict = {k:v for k,v in zip(result['key'], result['value'])}
    sorted_items = sorted(result_dict.items(), key=lambda x: int(x[0], 2))
    sorted_keys = [item[0] for item in sorted_items]
    sorted_values = [item[1] for item in sorted_items]

    ax = axs.flatten()[i]
    if i < num_subplots:
        ax.bar(range(len(sorted_keys)), sorted_values, tick_label=sorted_keys)
        ax.set_xlabel("")
        ax.set_ylabel("Value")
        ax.set_title('')
        ax.set_xticklabels(sorted_keys, rotation=45)
    else:
        ax.axis("off")

plt.tight_layout()
plt.show()





