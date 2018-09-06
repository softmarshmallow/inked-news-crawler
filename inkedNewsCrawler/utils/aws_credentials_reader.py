import csv
import json
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

def read_credentials(type = "json", credential='crawler_s3_access'):
    if type == "json":
        credentials_path_json = os.path.join(dir_path, "credentials/{}.json".format(credential))

        with open(credentials_path_json, 'r') as j:
            data = json.load(j)
            acc_key = data["Access key ID"]
            sec_key = data["Secret access key"]
            return acc_key, sec_key


#
# def import_credentials_first_time():
#     path = read_credentials_file_path_input()




if __name__ == "__main__":
    cred = read_credentials()
    print(cred)
