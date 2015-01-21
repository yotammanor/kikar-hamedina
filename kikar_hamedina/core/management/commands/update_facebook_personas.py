from django.core.management.base import BaseCommand

from django.contrib.contenttypes.models import ContentType

from facebook_feeds.models import Facebook_Persona
from polyorg.models import Candidate


class Command(BaseCommand):
    help = "Members that exist also as Candidates are updated to point to the candidates as well."

    def handle(self, *args, **options):
        print 'updating facebook_personas data'
        content_type = ContentType.objects.get(name='candidate')
        all_candidates = Candidate.objects.all()
        ids_of_persons_of_existing_candidates = [x.person_id for x in all_candidates]
        facebook_personas = Facebook_Persona.objects.all()
        personas_to_copy = [x for x in facebook_personas if x.object_id in ids_of_persons_of_existing_candidates]

        for persona in personas_to_copy:
            persona.alt_content_type = content_type
            persona.alt_content_type_id = content_type.id
            persona.alt_object_id = Candidate.objects.get(person__id=persona.object_id).id
            persona.alt_content_object = Candidate.objects.get(person__id=persona.object_id)
            persona.save()

        print 'done.'