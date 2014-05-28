__author__ = 'yotam'

from pprint import pprint
import json
import csv


json_data_facebook_feeds = open('data_fixture_facebook_feeds.json', mode='wb')

facebook_feed_csv = csv.DictReader(open('data_from_json_facebook_feeds.facebook_feed.csv', 'r'))
facebook_persona_csv = csv.DictReader(open(
    'data_from_json_facebook_feeds.facebook_persona.csv', 'r'))
tag_csv = csv.DictReader(open('data_from_json_facebook_feeds.tag.csv', 'r'))


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
    all_facebook_feeds_data_for_insertion = turn_csv_to_dict(facebook_persona_csv) + \
        turn_csv_to_dict(facebook_feed_csv)  # + \
        # turn_csv_to_dict(tag_csv)

    print 'creating facebook_feeds data fixture'
    pprint(all_facebook_feeds_data_for_insertion)
    json.dump(all_facebook_feeds_data_for_insertion, json_data_facebook_feeds, encoding='utf-8', indent=4)
    json_data_facebook_feeds.close()

if __name__ == "__main__":
    main()


