import logging
from facebook_feeds.management.commands.kikar_base_commands import KikarStatusCommand
from reporting.utils import TextProcessor


class Command(KikarStatusCommand):
    help = 'Retrieve all comments for a status, process content text and save to db..'

    def handle(self, *args, **options):
        """
        Executes fetchstatuslikes manage.py command.
        Receives either one status ID or filtering options for multiple statuses,
        and updates the likes data for status(es) selected.

        Options exist for running within a given date range.
        """

        list_of_statuses = self.parse_statuses(args, options)
        processor = TextProcessor()
        # Iterate over list_of_statuses
        for i, status in enumerate(list_of_statuses):
            self.stdout.write('working on status {} of {}'.format(i + 1, len(list_of_statuses)))
            if not status.comments.exists():
                self.stdout.write('No Comments found for status {}'.format(status.status_id))
                continue
            for j, comment in enumerate(status.comments.all()):
                self.stdout.write('\tworking on comment {} of {}'.format(j + 1, status.comments.count()))
                text = processor.text_manipulation_mk_names(text=comment.content, context_status=status)
                text = processor.text_manipulation_emojis(text=text)
                comment.processed_content = text
                comment.save()
        info_msg = "Successfully saved all statuses to db"
        logger = logging.getLogger('django')
        logger.info(info_msg)
        self.stdout.write('Successfully saved all statuses to db.')
