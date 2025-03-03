import json 
import os

folder_path = "./rand_light_back"

file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

data = {file_name: {"label": "000"} for file_name in file_names}

json_file = folder_path+"/background.json"

with open(json_file, 'w') as json_file:
    json.dump(data, json_file, indent=4)
