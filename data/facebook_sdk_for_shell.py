# coding: utf-8
import os
import facebook
from django.conf.settings import FACEBOOK_APP_ID, FACEBOOK_SECRET_KEY


graph = facebook.GraphAPI()
graph.access_token = facebook.get_app_access_token(FACEBOOK_APP_ID, FACEBOOK_SECRET_KEY)
graph.access_token = facebook.get_app_access_token(os.environ['FACEBOOK_APP_ID'], os.environ['FACEBOOK_SECRET_KEY'])
graph.get_object('508516607')
feed_id = input('feed_id')
select_self_published_status_query = """
select about, fan_count, name, page_id, username
from
page
where page_id={0}""".format(feed_id)

graph.fql(query=select_self_published_status_query)

api_request = "{0}/posts".format(feed_id)
args_for_request = {'limit':'20', 'fields': "from,message,id,created_time,updated_time,type,link,caption,picture,description,name,status_type,story,object_id,properties,source,to,shares,likes.summary(true).limit(1),comments.summary(true).limit(1)"}



page_details = '107836625941364/?fields=id,name,username,picture,about,birthday,website,link,likes,talking_about_count'
user_profile_details = '524575374?fields=id,name,picture,website,about,link,first_name,last_name,birthday'
# username deprecated for user_profile