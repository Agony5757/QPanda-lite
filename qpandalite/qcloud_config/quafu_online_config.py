import json
from pathlib import Path

def create_quafu_online_config(default_token = None,
                               savepath = None):    

    if not default_token:
        raise RuntimeError('You should input your token here.')

    if not savepath:
        savepath = Path.cwd()

    default_online_config = {
        'default_token' : default_token,
    }

    with open(savepath / 'quafu_online_config.json', 'w') as fp:
        json.dump(default_online_config, fp)

if __name__ == '__main__':
    
    # The quafu account token
    token = ''
    
    create_quafu_online_config(default_token = token)