import json
import datetime


def chunkify(big_list, chunk_size):
    chunks = [big_list[x:x + chunk_size] for x in range(0, len(big_list), chunk_size)]
    return chunks


def read_json(file_path):
    try:
        f = open(file_path)
        data = json.load(f)
        f.close()
    except Exception as e:
        print(e)
        data = []
    return data


def save_json(data, path):
    jsonString = json.dumps(data)
    jsonFile = open(path, "w")
    jsonFile.write(jsonString)
    jsonFile.close()


def jsonify(obj):
    if isinstance(obj, dict):
        return {k: jsonify(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [jsonify(el) for el in obj]
    elif isinstance(obj, datetime.date) or isinstance(obj, datetime.datetime):
        return str(obj)
    else:
        return obj


def extract_competition_info(file_name):
    splitted = file_name.split("_")
    stage = splitted[0] + "_" + splitted[1]
    match_day_str = splitted[2].split('.')[0]
    match_day = int(splitted[2].split('.')[0][1:])
    return stage, match_day_str, match_day
