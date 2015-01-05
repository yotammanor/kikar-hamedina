import shutil
import traceback
import os.path
import gzip
import tempfile
from optparse import make_option, OptionParser
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
    help = "Email a DB backup."

    option_list = BaseCommand.option_list + (
        make_option('-m',
                    '--mail-recipients',
                    type='string',
                    dest='recipients',
                    help='Mail addresses of recipients, comma-separated'),
        make_option('-f',
                    '--from-email',
                    default='kikar.backup@hasadna.org.il',
                    type='string',
                    dest='from_email',
                    help='From-email-address to use when sending email messages'),
        make_option('-a',
                    '--max-attachment-mb',
                    default=20*1024,
                    dest='max_attachment_mb',
                    type='int',
                    help='Max MBytes allowed per email attachment'),
    )

    start_time = timezone.now()

    def duration(self):
        return timezone.now() - self.start_time

    def create_backup(self, time_str, workdir, options):
        """Write a gzipped backup file, split into chunks if needed"""
        filename = os.path.join(workdir, 'kikardb_%s.gz' % (time_str, ))
        # Call dumpdata and write gzipped output
        with gzip.open(filename, 'wb') as f:
            call_command('dumpdata', use_base_manager=True, stdout=f)
            # call_command('dumpdata', 'facebook_feeds.facebook_persona', use_base_manager=True, stdout=f)
        max_size = options['max_attachment_mb'] * 1024 * 1024
        size = os.path.getsize(filename)
        n_parts = ((size - 1) / max_size) + 1
        if n_parts > 1:
            # Split into parts if there is more than one
            with open(filename, 'rb') as f:
                i_part = 0
                while size > 0:
                    i_part += 1
                    partfile = filename + '.%02dof%02d' % (i_part, n_parts)
                    print 'Creating', partfile
                    with open(partfile, 'wb') as pf:
                        size -= copy_bytes(f, pf, max_size)
            os.remove(filename)

    def send_backup_emails(self, workdir, time_str, recipients, from_email):
        """Send each backup file in a separate email"""
        files = os.listdir(workdir)

        for i, filename in enumerate(sorted(files)):
            path = os.path.join(workdir, filename)
            print "Sending file: %s (%.0f KB)" % (filename, os.path.getsize(path)/1024.0)
            body = ('Kikar Hamedina, backup at %s.\n' +
                    'File: %s.\n' +
                    'Process took %s.\n' +
                    'See attached backup file.\n') % (time_str, filename, self.duration())
            if len(files) > 1:
                # gunzipping a split file is a challenge - give the reader a tip
                body += '\nunzip with: cat %s.* | gunzip > data.json\n' % (os.path.splitext(filename)[0], )
            message = EmailMessage(subject='Kikar Hamedina backup %s (%d of %d)' % (time_str, i + 1, len(files)),
                                   body=body, to=recipients, from_email=from_email)
            message.attach_file(path)
            message.send()

    def send_error_email(self, msg, recipients, from_email):
        """Email an error report (used if something goes wrong)"""
        send_mail(subject='Kikar Hamedina backup error',
                  message='Kikar Hamedina backup failed after %s. Error:\n\n%s' % (self.duration(), msg),
                  from_email=from_email,
                  recipient_list=recipients)

    def handle(self, *args, **options):
        recipients = [s.strip() for s in options['recipients'].split(',')]
        if not recipients:
            raise CommandError('No recipients specified (use -m or --mail-recipients)')
        from_email = options['from_email']

        time_str = timezone.now().strftime('%Y%m%d_%H%M')

        try:
            print 'Creating backup files'
            workdir = tempfile.mkdtemp()
            try:
                self.create_backup(time_str, workdir, options)
                print 'Emailing backup files'
                self.send_backup_emails(workdir, time_str, recipients, from_email)
            finally:
                print 'Cleaning up work dir %s' % (workdir, ) 
                shutil.rmtree(workdir)
        except Exception as e:
            print 'ERROR:', e
            print 'Sending error email'
            self.send_error_email(traceback.format_exc(), recipients, from_email)
            raise

        print 'Done (duration %s)' % (self.duration(), )
