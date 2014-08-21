
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
    countries = {}

    for key in keys:
        print key

        r = requests.get(BASE + "/data/" + key)
        data = r.json()
        parts = data["id"].split("/")
        parts.pop(0)
        country = parts[0]

        parsed_data = map_data(data)

        if len(parts) == 1:
            countries[country] = parsed_data

        elif len(parts) == 2:
            if "areas" not in countries[country]:
                countries[country]["areas"] = {}

            countries[country]["areas"][parts[1]] = parsed_data

        elif len(parts) == 3:
            if "localities" not in countries[country]["areas"][parts[1]]:
                countries[country]["areas"][parts[1]]["localities"] = {}

            countries[country]["areas"][parts[1]]["localities"][parts[2]] = parsed_data

        elif len(parts) == 4:
            if "sublocalities" not in countries[country]["areas"][parts[1]]["localities"][parts[2]]:
                countries[country]["areas"][parts[1]]["localities"][parts[2]]["sublocalities"] = {}

            countries[country]["areas"][parts[1]]["localities"][parts[2]]["sublocalities"][parts[3]] = parsed_data

    return countries

FIELDS = {
    "R": "COUNTRY",
    "S": "ADMINISTRATIVE_AREA",
    "C": "LOCALITY",
    "D": "DEPENDENT_LOCALITY",
    "Z": "POSTAL_CODE",
    "X": "SORTING_CODE",
    "1": "ADDRESS_LINE_1",
    "2": "ADDRESS_LINE_2",
    "3": "ADDRESS_LINE_3",
}

def map_field_list(field_spec):
    fields = []
    for c in field_spec:
        fields.append(FIELDS[c])

    return fields

def map_data(data):
    keys = []

    keys.append(("name", data["name"]))

    if "fmt" in data:
        keys.append(("format", data["fmt"]))

    if "upper" in data:
        keys.append(("upper", map_field_list(data["upper"])))

    if "required" in data:
        keys.append(("upper", map_field_list(data["upper"])))

    if "state_name_type" in data:
        keys.append(("area_name_type", data["state_name_type"]))

    if "zip" in data:
        keys.append(("postal_code_format", data["zip"]))

    if "zipex" in data:
        keys.append(("postal_code_examples", data["zipex"].split(",")))

    return OrderedDict(keys)


def _dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())
yaml.SafeDumper.add_representer(OrderedDict, _dict_representer)

keys = get_keys()

print yaml.safe_dump(get_data(keys[:5]), default_flow_style=False)
