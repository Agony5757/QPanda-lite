import qpandalite.task.originq as origin

taskid = '646341A5137A4CE4B0A662618999E0C0'

result = origin.query_by_taskid(taskid)
# print(result)
print(result['status'])
print(result['result'])