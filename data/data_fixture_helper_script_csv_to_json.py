__author__ = 'yotam'

from pprint import pprint
import json
import csv


json_data = open('data_fixture.json', mode='wb')
party_csv = csv.DictReader(open('data_from_json_core.party.csv', 'r'))
person_csv = csv.DictReader(open('data_from_json_core.person.csv', 'r'))
facebook_feed_csv = csv.DictReader(open('data_from_json_core.facebook_feed.csv', 'r'))
tag_csv = csv.DictReader(open('data_from_json_core.tag.csv', 'r'))


def turn_csv_to_dict(dict_reader_object):
    list_of_dicts_for_insertion = []
    for row in dict_reader_object:
        full_dict = dict()
        full_dict['pk'] = row.pop('pk')
        full_dict['model'] = row.pop('model')
        fields_dict = dict()
        for key, value in row.items():
            fields_dict[key] = value
        full_dict['fields'] = fields_dict
        list_of_dicts_for_insertion.append(full_dict)

    pprint(list_of_dicts_for_insertion)
    return list_of_dicts_for_insertion


def main():
    all_data_for_insertion = turn_csv_to_dict(party_csv) + \
        turn_csv_to_dict(person_csv) + \
        turn_csv_to_dict(facebook_feed_csv) + \
        turn_csv_to_dict(tag_csv)

    pprint(all_data_for_insertion)
    json.dump(all_data_for_insertion, json_data, encoding='utf-8')
    json_data.close()


if __name__ == "__main__":
    main()


