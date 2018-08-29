import csv
import json
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
credentials_path_json = os.path.join(dir_path, "credentials/crawler_s3_access.json")
credentials_path_csv = os.path.join(dir_path, "credentials/crawler_s3_access.csv")

def read_credentials(type = "json"):
    if type == "json":
        with open(credentials_path_json, 'r') as j:
            data = json.load(j)
            acc_key = data["Access key ID"]
            sec_key = data["Secret access key"]
            return acc_key, sec_key
    elif type == "csv":
        with open(credentials_path_csv) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                print(row)
                print(row[0])
                print(row[0],row[1],row[2],)
        raise NotImplementedError


#
# def import_credentials_first_time():
#     path = read_credentials_file_path_input()




if __name__ == "__main__":
    cred = read_credentials()
    print(cred)
