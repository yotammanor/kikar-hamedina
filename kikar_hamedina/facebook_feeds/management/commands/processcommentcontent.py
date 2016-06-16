import logging
from facebook_feeds.management.commands.kikar_base_commands import KikarStatusCommand
from facebook_feeds.models import Facebook_Status_Comment
from reporting.utils import TextProcessor
from concurrent import futures


class Command(KikarStatusCommand):
    help = 'Retrieve all comments for a status, process content text and save to db..'

    def worker(self, i, comment, status, processor):
        self.stdout.write('working on comment {}'.format(i))
        text = processor.text_manipulation_mk_names(text=comment.content, context_status=status)
        text = processor.text_manipulation_emojis(text=text)
        comment.processed_content = text
        comment.save()

    def handle(self, *args, **options):
        """
        Executes processcommentcontent manage.py command.
        Receives one or more status ids.
        takes all comments for status(es) and saves processed_content field after text manipulation.
        """

        list_of_statuses = self.parse_statuses(args, options)
        processor = TextProcessor()
        # Iterate over list_of_statuses
        i = 1
        if not options['workers']:
            for status in list_of_statuses:
                for comment in status.comments.all():
                    self.worker(i, comment, status, processor)
                    i += 1
        else:
            with futures.ThreadPoolExecutor(max_workers=options['workers']) as executer:
                for status in list_of_statuses:
                    for comment in status.comments.all():
                        executer.submit(self.worker, i, comment, status, processor)
                        i += 1
        info_msg = "Successfully saved all statuses to db"
        logger = logging.getLogger('django')
        logger.info(info_msg)
        self.stdout.write('Successfully saved all statuses to db.')
