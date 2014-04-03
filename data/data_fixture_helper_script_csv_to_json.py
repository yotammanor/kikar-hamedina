__author__ = 'yotam'

from pprint import pprint
import json
import csv


json_data_core = open('data_fixture_core.json', mode='wb')
json_data_persons = open('data_fixture_persons.json', mode='wb')

party_csv = csv.DictReader(open('data_from_json_persons.party.csv', 'r'))
person_csv = csv.DictReader(open('data_from_json_persons.person.csv', 'r'))
facebook_feed_csv = csv.DictReader(open('data_from_json_core.facebook_feed.csv', 'r'))
facebook_feed_generic_csv = csv.DictReader(open('data_from_json_core.facebook_feed_generic.csv', 'r'))
tag_csv = csv.DictReader(open('data_from_json_core.tag.csv', 'r'))


def turn_csv_to_dict(dict_reader_object):
    list_of_dicts_for_insertion = []
    for row in dict_reader_object:
        full_dict = dict()
        full_dict['pk'] = row.pop('pk')
        full_dict['model'] = row.pop('model')
        fields_dict = dict()
        for key, value in row.items():
            if key == 'content_type':
                fields_dict[key] = eval(value)
            else:
                fields_dict[key] = value
        full_dict['fields'] = fields_dict
        list_of_dicts_for_insertion.append(full_dict)

    pprint(list_of_dicts_for_insertion)
    return list_of_dicts_for_insertion


def main():
    all_persons_data_for_insertion =  turn_csv_to_dict(party_csv) + \
        turn_csv_to_dict(person_csv)

    all_core_data_for_insertion = turn_csv_to_dict(facebook_feed_generic_csv) + \
        turn_csv_to_dict(facebook_feed_csv) + \
        turn_csv_to_dict(tag_csv)

    print 'creating persons data fixture'
    pprint(all_persons_data_for_insertion)
    json.dump(all_persons_data_for_insertion, json_data_persons, encoding='utf-8')
    json_data_persons.close()

    print 'creating core data fixture'
    pprint(all_core_data_for_insertion)
    json.dump(all_core_data_for_insertion, json_data_core, encoding='utf-8')
    json_data_core.close()



if __name__ == "__main__":
    main()


