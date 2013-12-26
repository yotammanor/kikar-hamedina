Installation
==============

.. Set the following environment variables:

- DJANGO_SETTINGS_MODULE (for local version set 'kikar_hamedina.settings.local')
- SECRET_KEY
- FACEBOOK_SECRET_KEY
- FACEBOOK_APP_ID

.. Set your db inside ``kikar_hamedina/kikar_hamedina/settings/base.py`` with your db details.

<<<<<<< HEAD
.. Install required packages: ``pip install -r requirements/local.txt`` (for local version requirements)
=======
Install required packages: ``pip install -r requirements/local.txt`` (for local version requirements)



Once you're all setup run:
python manage.py runserver
Go to localhost:8000/admin, log in and add Persons, Parties and Feeds.
Get vendor id for a feed as follows:
For Yair Lapid, find his page:
https://www.facebook.com/YairLapid

The last part of the above URL is important. Take YairLapid and search for it using the Facebook explorer:
https://developers.facebook.com/tools/explorer?method=GET&path=YairLapid%3Ffields%3Did%2Cname

The id returned by the query is the vendor_id.

Then run the command:
python manage.py fetchfeed

The above downloads all feeds. You can also run:
python manage.py fetchfeed {feed_id}
to download a single feed.
>>>>>>> c70a69eba98426046486e36e552fa875cefbfbec
