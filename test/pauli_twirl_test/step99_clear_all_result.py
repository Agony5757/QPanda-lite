import shutil
from pathlib import Path
import datetime
import os

path = 'quafu' + '_online_info_verify'
savepath = Path.cwd() / path

if os.path.exists(savepath):
    datetime_str = datetime.datetime.now().strftime(r'%Y%m%d-%H%M%S')
    history_path = Path.cwd() / 'history' / f'{path}_{datetime_str}'
    shutil.move(savepath, history_path)
    print('Successfully clear outputs!')
else:
    print('No existing file!')
