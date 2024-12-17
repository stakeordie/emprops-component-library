import json
import requests
import io
import base64
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-m", "--model", help="Model To Load", default="sd_xl_base_1.0")

args = parser.parse_args()

url = "http://127.0.0.1:3130" # or your URL
opt = requests.get(url=f'{url}/sdapi/v1/options')
opt_json = opt.json()
opt_json['sd_model_checkpoint'] = args.model
requests.post(url=f'{url}/sdapi/v1/options', json=opt_json)