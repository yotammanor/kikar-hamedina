import json
import logging
import pprint
from urllib2 import urlopen
from urllib import urlencode
from optparse import make_option
from datetime import datetime
from unidecode import unidecode
from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

from mks.models import Knesset, Party, Member


SOURCE_API_URL = getattr(settings, 'SOURCE_API_URL', 'http://oknesset.org/api')
SOURCE_API_VERSION = getattr(settings, 'SOURCE_API_VERSION', 'v2')
DEFAULT_SOURCE_ARGS = getattr(settings, 'DEFAULT_SOURCE_ARGS', {'format': 'json'})
DATE_FORMAT_AT_SOURCE = getattr(settings, 'DATE_FORMAT_AT_SOURCE', '%Y-%m-%d')


LIST_INDEX_START = 0
SLEEP_TIME = 9


class Command(BaseCommand):
    args = '<member_id>'
    help = 'Update mks data from source through api'

    option_list = BaseCommand.option_list + (
        make_option('-f',
                    '--force-update',
                    action='store_true',
                    dest='force-update',
                    default=False,
                    help='Force update of member.'),
        make_option('-n',
                    '--noinput',
                    action='store_true',
                    dest='noinput',
                    default=False,
                    help='no input from user requested. runs in safe-mode unless flagged otherwise.'),
        make_option('-s',
                    '--unsafe-mode',
                    action='store_true',
                    dest='unsafe-mode',
                    default=False,
                    help='When running in un-safe mode and noinput mode, all promts are treated as (Y)es.'),
        make_option('-p',
                    '--party-mode',
                    action='store_true',
                    dest='party-mode',
                    default=False,
                    help='Update party data.'),
        make_option('-m',
                    '--new-mks-only',
                    action='store_true',
                    dest="new_mks_only",
                    default=False,
                    help="update only missing mks, without updating data")

    )

    def get_request_from_source(self, resource_name, resource_value=None, args=DEFAULT_SOURCE_ARGS):
        request_url = "{url}/{api_version}/{resource_name}".format(url=SOURCE_API_URL,
                                                                   api_version=SOURCE_API_VERSION,
                                                                   resource_name=resource_name)
        if resource_value:
            request_url += "/{resource_value}/".format(resource_value=resource_value)

        if args:
            request_url += "?{encoded_args}".format(encoded_args=urlencode(args))

        # print request_url
        parsed_request = json.load(urlopen(request_url))
        return parsed_request

    def remove_redundant_object(self, object_id, object_type, is_yes_for_all):
        model = get_model('mks', object_type)
        try:
            object_for_removal = model.objects.get(id=object_id)
        except Member.DoesNotExist:
            raise

        input_value = ''
        if not is_yes_for_all:
            input_value = raw_input('Do you want to delete member: %s, %s? press Y for Yes, any other key for No.' % (
            object_id, object_for_removal))

        if is_yes_for_all or input_value == 'Y':
            print 'deleting member %s' % object_id
            object_for_removal.delete()

    def inspect_list_of_all_objects(self, list_of_object_id, object_type, options):
        """
        This function compares local list of members with list as appears on source.
        It offers to add new members, or delete deprecated members,
        and returns the updated list of members for update later on.
                """
        is_yes_for_all = options['noinput'] & options['unsafe-mode']

        set_of_local_objects = set(list_of_object_id)
        set_of_source_objects = set([obj['id'] for obj in self.get_request_from_source(object_type)['objects']])

        redundant_objects = set_of_local_objects - set_of_source_objects
        missing_objects = set_of_source_objects - set_of_local_objects
        print 'redundant_objects:', redundant_objects
        print 'missing_objects:', missing_objects

        if not options['noinput'] or is_yes_for_all:
            for object_id in redundant_objects:
                self.remove_redundant_object(object_id, object_type, is_yes_for_all)

        print 'exist in both:', set_of_local_objects & set_of_source_objects

        if options['new_mks_only']:
            return list(missing_objects)
        return list((set_of_local_objects - redundant_objects) | missing_objects)
        # return list(missing_objects)

    def format_date(self, date_string, date_format=DATE_FORMAT_AT_SOURCE):
        try:
            start_date = datetime.strptime(date_string, date_format).date()
        except ValueError:
            start_date = None
        except TypeError:
            start_date = None
        return start_date

    def update_member_instance(self, member_id):

        member_from_source = self.get_request_from_source('member', member_id)
        # pprint.pprint(member_from_source.keys())

        if not member_from_source['gender']:
            parsed_gender_value = None
        elif unidecode(member_from_source['gender']) == 'zkr':
            parsed_gender_value = 'M'
        else:  # nqbh
            parsed_gender_value = 'F'

        local_member, created = Member.objects.get_or_create(id=member_id)
        if created:
            print 'Yay, new mk was added!'
        # pprint.pprint(dir(local_member))
        local_member.name_he = member_from_source['name']
        local_member.current_position = member_from_source['current_position']
        local_member.start_date = self.format_date(member_from_source['start_date'])
        local_member.end_date = self.format_date(member_from_source['end_date'])
        local_member.img_url = member_from_source['img_url']
        local_member.phone = member_from_source['phone']
        local_member.fax = member_from_source['fax']
        local_member.email = member_from_source['email']
        local_member.family_status = member_from_source['family_status']
        local_member.number_of_children = member_from_source['number_of_children']
        local_member.date_of_birth = self.format_date(member_from_source['date_of_birth'])
        local_member.place_of_birth = member_from_source['place_of_birth']

        party_id = member_from_source['party_url'].split('/')[2]  # splitting: u'/party/29/'
        print 'party_id extracted:', party_id
        try:
            party = Party.objects.get(id=party_id)
            party.members.add(local_member)
        except:
            print 'missing party id in db'
            pass

        local_member.date_of_death = self.format_date(member_from_source['date_of_death'])
        local_member.year_of_aliyah = member_from_source['year_of_aliyah']
        local_member.is_current = member_from_source['is_current']
        local_member.place_of_residence = member_from_source['place_of_residence']
        local_member.place_of_residence_lat = member_from_source['place_of_residence_lat']
        local_member.place_of_residence_lon = member_from_source['place_of_residence_lon']
        local_member.residence_centrality = member_from_source['residence_centrality']
        local_member.residence_economy = member_from_source['residence_economy']
        local_member.gender = parsed_gender_value

        local_member.current_role_descriptions = member_from_source['current_role_descriptions']
        local_member.bills_stats_proposed = member_from_source['bills_stats_proposed']
        local_member.bills_stats_pre = member_from_source['bills_stats_pre']
        local_member.bills_stats_first = member_from_source['bills_stats_first']
        local_member.bills_stats_approved = member_from_source['bills_stats_approved']
        local_member.average_weekly_presence_hours = member_from_source['average_weekly_presence_hours']
        local_member.average_monthly_committee_presence = member_from_source['average_monthly_committee_presence']

        # Data unavailable through api

        # local_member.parties = member_from_source['parties']
        # local_member.current_party = member_from_source['current_party']
        # local_member.website = member_from_source['website']
        # local_member.blog = member_from_source['blog']
        # local_member.area_of_residence = member_from_source['area_of_residence']
        # local_member.user = member_from_source['user']
        # local_member.backlinks_enabled = member_from_source['backlinks_enabled']

        print ' Saving %s to db..' % member_id,
        local_member.save()
        print 'done.'

    def update_party_instance(self, party_id, options):
        party_from_source = self.get_request_from_source('party', party_id)
        # pprint.pprint(party_from_source.keys())
        local_party, created = Party.objects.get_or_create(id=party_id)

        local_party.name = party_from_source['name']
        local_party.is_coalition = party_from_source['is_coalition']
        local_party.number_of_members = party_from_source['number_of_members']
        local_party.knesset = Knesset.objects.get(number=party_from_source['knesset_id'])
        local_party.logo = party_from_source['logo']

        # Data unavailable through api

        # local_party.start_date = self.format_date(party_from_source['start_date'])
        # local_party.end_date = self.format_date(party_from_source['end_date'])
        # local_party.number_of_seats = party_from_source['number_or_seats']

        print ' Saving %s to db..' % party_id,
        local_party.save()
        print 'done.'

    def handle(self, *args, **options):
        """

        """

        # update party data

        if options['party-mode']:
            print "it's party time!"
            list_of_parties = Party.current_knesset.all()
            list_of_party_ids = [party.id for party in list_of_parties]
            list_of_party_ids = self.inspect_list_of_all_objects(list_of_party_ids, 'party', options)

            for i, party_id in enumerate(list_of_party_ids):
                print 'working on %d of %d: party: %s' % (i + 1, len(list_of_party_ids), party_id)
                self.update_party_instance(party_id, options)
                sleep(SLEEP_TIME)

        # update members data
        else:
            list_of_members = list()
            test_for_all_members = False

            # Case no args - fetch all Members
            if len(args) == 0:
                list_of_members = list(Member.objects.all())
                test_for_all_members = True

            # Case arg exists - fetch Member by id supplied
            elif len(args) == 1:
                member_id = args[0]
                try:
                    member = Member.objects.get(id=member_id)
                    list_of_members.append(member)

                except Member.DoesNotExist:
                    warning_msg = "Status #({0}) does not exist.".format(member_id)
                    logger = logging.getLogger('django')
                    logger.warning(warning_msg)
                    raise CommandError(
                        'Member "%s" does not exist. If you know it to exist in oknesset.org, run with no parameters and it will be added automatically.' % member_id)

            # Case invalid args
            else:
                raise CommandError('Please enter a valid status id')

            list_of_member_ids = [member.id for member in list_of_members]

            # if executed as update for all members, test for gaps between source and local.
            if test_for_all_members:
                list_of_member_ids = self.inspect_list_of_all_objects(list_of_member_ids, 'member', options)
                print list_of_member_ids

            # Iterate over list_of_members of direct update on selected members
            for i, member_id in enumerate(list_of_member_ids[LIST_INDEX_START:]):
                print 'working on %d of %d: member: %s' % (i + LIST_INDEX_START + 1, len(list_of_member_ids[LIST_INDEX_START:]), member_id),
                self.update_member_instance(member_id)
                print 'sleep for %d secs' % SLEEP_TIME
                sleep(SLEEP_TIME)

        print 'Done.'