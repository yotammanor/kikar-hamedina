from django.core.management.base import BaseCommand, CommandError
from updater import models

class Command(BaseCommand):
    help ='Running all the rules on the relevant posts and updates subscribers'
    def handle(self, *args, **options):
        for rule in models.rulesContainer.rules:
            for ruleObj in rule.objects.all():
                ruleObj.handle_new_posts()