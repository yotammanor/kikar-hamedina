# coding: utf-8
import os
import facebook
import facebook
graph = facbook.GraphAPI()
graph = facebook.GraphAPI()
graph.access_token = facebook.get_app_access_token(os.environ['FACEBOOK_APP_ID'], os.environ['FACEBOOK_SECRET_KEY'])
get_ipython().magic(u'pinfo graph')
graph.get_object('508516607')
feed_id = input('feed_id')
select_self_published_status_query = """
select about, fan_count, name, page_id, username
from
page
where page_id={0}""".format(feed_id)

graph.fql(query=select_self_published_status_query)
