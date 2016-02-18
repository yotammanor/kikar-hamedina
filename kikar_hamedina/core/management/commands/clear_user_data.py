import shutil
import traceback
import os.path
import gzip
import tempfile
from optparse import make_option, OptionParser

from django.contrib.auth.models import User
from time import sleep


from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
import django.core.management.commands.dumpdata as dumpdata

def copy_bytes(in_file, out_file, max_bytes):
    """Copy up max_bytes from in_file to out_file. If there are not enough
    bytes - copy until EOF"""
    bytes_read = 0
    while max_bytes > bytes_read:
        buf = in_file.read(min(16*1024, max_bytes - bytes_read))
        if buf == "":
            break
        out_file.write(buf)
        bytes_read += len(buf)
    return bytes_read

class Command(BaseCommand):
    help = "Clear user data from db"

    start_time = timezone.now()

    def duration(self):
        return timezone.now() - self.start_time


    def handle(self, *args, **options):
        users = User.objects.all().exclude(username='admin')
        for i, user in enumerate(users):
            print 'working on user: ', i
            user.username = 'janeDoe' + str(user.id)
            user.first_name = 'Jane'
            user.last_name = 'Doe'
            user.email = ''
            user.is_staff = False
            user.is_superuser = False
            user.is_active = False
            user.save()

        print 'Done (duration %s)' % (self.duration(), )
