__author__ = 'yotam'

import json
import csv
from pprint import pprint



json_data = json.load(open('data_fixture_persons.json', mode='r'))  # insert name of json
person_dict = [x for x in json_data if x['model'] == 'persons.person']
person_altname_dict = [x for x in json_data if x['model'] == 'persons.personaltname']
title_dict = [x for x in json_data if x['model'] == 'persons.title']


all_dicts = [person_dict, title_dict, person_altname_dict]


def insert_to_csv(chosen_dict):
    print 'chosen_dict:', chosen_dict
    field_names = chosen_dict[0].keys()[:-1]
    for field in chosen_dict[0]['fields'].keys():
        field_names.append(field)
    print field_names
    flat_dict_list = []
    for dict_object in chosen_dict:
        flat_dict = {}
        for key in dict_object.keys()[:-1]:
            if type(dict_object[key]) == str:
                flat_dict[key] = dict_object[key]
            elif type(dict_object[key]) == list:
                flat_dict[key] = str(dict_object[key])
            else:
                flat_dict[key] = dict_object[key]
        for key in dict_object['fields'].keys():
            if type(dict_object['fields'][key]) == str:
                flat_dict[key] = dict_object['fields'][key]
            else:
                flat_dict[key] = dict_object['fields'][key]
        flat_dict_list.append(flat_dict)
    pprint(flat_dict_list)

    file_name = 'data_from_json_%s.csv' % chosen_dict[0]['model']
    output_file = open(file_name, mode='wb')
    csv_data = csv.DictWriter(output_file, field_names)
    headers = {field_name: field_name for field_name in field_names}
    csv_data.writerow(headers)
    for flat_dict in flat_dict_list:
        print flat_dict
        csv_data.writerow({k: unicode(v).encode('utf-8') for k, v in flat_dict.items()})
    output_file.close()

for json_dict in all_dicts:
    insert_to_csv(json_dict)




