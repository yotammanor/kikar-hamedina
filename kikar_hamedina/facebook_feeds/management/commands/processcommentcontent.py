import logging
from facebook_feeds.management.commands.kikar_base_commands import KikarStatusCommand
from reporting.utils import TextProcessor
from concurrent import futures


class Command(KikarStatusCommand):
    help = 'Retrieve all comments for a status, process content text and save to db..'

    def worker(self, j, comment, status, processor):
        self.stdout.write('\tworking on comment {} of {}'.format(j + 1, status.comments.count()))
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
        for i, status in enumerate(list_of_statuses):
            self.stdout.write('working on status {} of {}'.format(i + 1, len(list_of_statuses)))
            if not status.comments.exists():
                self.stdout.write('No Comments found for status {}'.format(status.status_id))
                continue
            with futures.ThreadPoolExecutor(max_workers=options['workers']) as executer:
                [executer.submit(self.worker, j, comment, status, processor) for j, comment in
                 enumerate(status.comments.all())]
        info_msg = "Successfully saved all statuses to db"
        logger = logging.getLogger('django')
        logger.info(info_msg)
        self.stdout.write('Successfully saved all statuses to db.')
