from django.core.management.base import BaseCommand
import networkx as nx

from facebook_feeds.models import Facebook_Status_Comment, Facebook_User, Facebook_Feed


class Command(BaseCommand):
    def create_graph(self):
        G = nx.Graph()
        i = 1
        for facebook_user in Facebook_User.objects.all()[:10]:
            print(i)
            G.add_node(facebook_user.facebook_id, type='user', object=facebook_user)
            for feed in Facebook_Feed.objects.all():
                G.add_node(feed.id, type='mk', object=feed)
                num_of_comments = facebook_user.comments.filter(parent__feed__id=feed.id).count()
                G.add_edge(facebook_user.facebook_id, feed.id, weight=num_of_comments)
            i += 1

    def handle(self, *args, **options):
        print('start.')
        self.create_graph()
        print('done.')
