__author__ = 'yotam'

from pprint import pprint
import json
import csv


json_data_mks = open('../mks/data_fixture_mks.json', mode='wb')

knesset_csv = csv.DictReader(open('../mks/data_from_json_mks.knesset.csv', 'r'))
party_csv = csv.DictReader(open('../mks/data_from_json_mks.party.csv', 'r'))
member_csv = csv.DictReader(open('../mks/data_from_json_mks.member.csv', 'r'))
coalitionmembership_csv = csv.DictReader(open('../mks/data_from_json_mks.coalitionmembership.csv', 'r'))
memberaltname_csv = csv.DictReader(open('../mks/data_from_json_mks.memberaltname.csv', 'r'))
membership_csv = csv.DictReader(open('../mks/data_from_json_mks.membership.csv', 'r'))
weeklypresence_csv = csv.DictReader(open('data_from_json_mks.weeklypresence.csv', 'r'))

all_csv = [knesset_csv, party_csv, member_csv, coalitionmembership_csv, memberaltname_csv, membership_csv,
           weeklypresence_csv]


def turn_csv_to_dict(dict_reader_object):
    list_of_dicts_for_insertion = []
    for row in dict_reader_object:
        full_dict = dict()
        full_dict['pk'] = row.pop('pk')
        full_dict['model'] = row.pop('model')
        fields_dict = dict()
        for key, value in row.items():
            if key == 'content_type' or value == 'None':
                fields_dict[key] = eval(value)
            elif value == "TRUE":
                fields_dict[key] = True
            elif value == "FALSE":
                fields_dict[key] = False
            else:
                fields_dict[key] = value
        full_dict['fields'] = fields_dict
        list_of_dicts_for_insertion.append(full_dict)

    pprint(list_of_dicts_for_insertion)
    return list_of_dicts_for_insertion


def main():
    all_mks_data_for_insertion = list()
    for csv_data in all_csv:
        all_mks_data_for_insertion += turn_csv_to_dict(csv_data)

    print 'creating mks data fixture'
    pprint(len(all_mks_data_for_insertion))
    json.dump(all_mks_data_for_insertion, json_data_mks, encoding='utf-8', indent=4)
    json_data_mks.close()


if __name__ == "__main__":
    main()


