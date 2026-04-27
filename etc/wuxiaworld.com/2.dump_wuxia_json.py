#!/usr/bin/env python3
import json
import sys
import argparse
from pathlib import Path
from pyease_grpc import Protobuf

input_path = Path(r"proto_temp") / 'wuxia.proto'

def dump_json():
    output_path = input_path.parent.parent / f'{input_path.stem}.json'
    protobuf_ = Protobuf.from_file(str(input_path),[str(input_path.parent)])
    json_ = json.dumps(protobuf_.save())
    with open(output_path, "w") as f:
        f.write(json_)
        
def dump_prety_json():
    output_path = input_path.parent.parent / f'{input_path.stem}.json'
    protobuf_ = Protobuf.from_file(str(input_path),[str(input_path.parent)])
    json_ = json.dumps(protobuf_.save(),indent=4)
    with open(output_path, "w") as f:
        f.write(json_)

def dump_wuxiacom_proto():
    output_path = input_path.parent.parent / 'wuxiacom_proto.py'
    protobuf_ = Protobuf.from_file(str(input_path),[str(input_path.parent)])
    json_ = json.dumps(protobuf_.save())
    wuxiacom_proto_string = (
            'import json;' + '\n'
            f'WUXIWORLD_PROTO__str = """{json_}""";' + '\n'
            'WUXIWORLD_PROTO = json.loads(WUXIWORLD_PROTO__str);' + '\n'
            )
    with open(output_path, "w") as f:
        f.write(wuxiacom_proto_string)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', nargs='?', const=True, default=False)
    parser.add_argument('-json-prety', nargs='?', const=True, default=False)
    args = parser.parse_args()

    if args.json:
        dump_json()
    elif args.json_prety:
        dump_prety_json()
    else:
        dump_wuxiacom_proto()
if __name__ == '__main__':
    main()
