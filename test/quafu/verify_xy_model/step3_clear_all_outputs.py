import shutil
from pathlib import Path
import datetime 
import os
savepath = Path.cwd() / 'quafu_online_info_verify'

if os.path.exists(savepath):
    datetime_str = datetime.datetime.now().strftime(r'%Y%m%d-%H%M%S')
    history_path = Path.cwd() / 'history' / f'quafu_online_info_verify_{datetime_str}'
    shutil.move(savepath, history_path)
    print('Successfully clear outputs!')
else:
    print('No existing file!')
