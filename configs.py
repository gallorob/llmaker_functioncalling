import types
from argparse import Namespace

import yaml

with open(f'configs.yml', 'r') as file:
    configs: Namespace = Namespace(**yaml.safe_load(file))
    with open(f'secret', 'r') as f:
        configs.openai_api_key = f.read().strip()
