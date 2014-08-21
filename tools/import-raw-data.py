
import requests
import yaml
import re
from collections import OrderedDict

BASE = "http://i18napis.appspot.com/address"


def get_keys():
    r = requests.get(BASE)

    pattern = re.compile("<a href=\'/address/data/(.*)\'>")

    keys = set([])
    for m in pattern.finditer(r.text):
        keys.add(m.group(1))

    return sorted(keys)

def get_data(keys):
    data = {}

    for key in keys:
        print repr(key)

        r = requests.get(BASE + "/data/" + key)
        data[key] = r.json()

    return data


def _dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())
yaml.SafeDumper.add_representer(OrderedDict, _dict_representer)

keys = get_keys()

with open("raw.yaml", "wb") as f:
    f.write(yaml.safe_dump(get_data(keys), default_flow_style=False))
