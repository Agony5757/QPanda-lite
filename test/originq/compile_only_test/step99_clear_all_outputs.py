import shutil
from pathlib import Path
import datetime 
import os
from step1_submit_circuit import savepath
from step3_plot_timeline import figure_save_path

datetime_str = datetime.datetime.now().strftime(r'%Y%m%d-%H%M%S')

history_path = Path.cwd() / 'history' / f'origin_online_info_verify_{datetime_str}'

if os.path.exists(savepath):
    shutil.move(savepath, history_path)
else:
    print('No existing online_info file!')

history_path = Path.cwd() / 'history' / f'timeline_plot_{datetime_str}'

if os.path.exists(figure_save_path):
    shutil.move(figure_save_path, history_path)    
else:
    print('No existing timeline_plot file!')

    print('Successfully clear outputs!')