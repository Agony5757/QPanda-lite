import json
from pathlib import Path

if __name__ == '__main__':
    
    default_token = None
    # default_token = ' INPUT YOUR TOKEN HERE '
    if not default_token:
        raise RuntimeError('You should input your token here.')

    default_online_config = {
            'default_token' : default_token,
        }
    with open(Path.cwd() / 'quafu_online_config.json', 'w') as fp:
        json.dump(default_online_config, fp)