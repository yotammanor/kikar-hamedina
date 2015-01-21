__author__ = 'yotam'

import json
import csv
from pprint import pprint



json_data = json.load(open('data_fixture_facebook_feeds.json', mode='r'))  # insert name of json
facebook_persona_dict = [x for x in json_data if x['model'] == 'facebook_feeds.facebook_persona']
facebook_feed_dict = [x for x in json_data if x['model'] == 'facebook_feeds.facebook_feed']
tag_dict = [x for x in json_data if x['model'] == 'facebook_feeds.tag']

all_dicts = [facebook_persona_dict,
             facebook_feed_dict,
             tag_dict
]


def insert_to_csv(chosen_dict):
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

for i, json_dict in enumerate(all_dicts):
    print '%d of %d' % (i+1, len(all_dicts))
    if json_dict:
        insert_to_csv(json_dict)
    else:
        print 'json file empty'

print len(facebook_persona_dict), \
    len(facebook_feed_dict), \
    len(tag_dict)


