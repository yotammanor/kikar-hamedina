Installation
==============

.. Set the following environment variables:

- DJANGO_SETTINGS_MODULE (for local version set 'kikar_hamedina.settings.local')
- SECRET_KEY
- FACEBOOK_SECRET_KEY
- FACEBOOK_APP_ID

.. Set your db inside ``kikar_hamedina/kikar_hamedina/settings/local.py`` with your db details.

.. Install required packages: ``pip install -r requirements/local.txt`` (for local version requirements)



To insert initial data into the db, do as follows:

``python manage.py loaddata data_fixture.json`` - Note that the ``core_*`` tables in the db need to be truncated first. 

``python fetchfeed --initial``

The first command will insert to db data from a pre-created list of parties, persons, feeds, and tags.
The second command will fetch statuses for all feeds in data. Tag initial sets the request to 500 messages per feed (as opposed to default of 20), so it might take a while to finish. 


You can also run: ``python manage.py fetchfeed {feed_id} [--initial]`` to download a single feed.



Once you're all setup run:

``python manage.py runserver``

and enjoy the show.




Editing data_fixture:

At the main directory there's a sub-directory called data. Within it there are four csv files, for Party, Person, Feed, and Tag data, which can be edited.

* Note that in order to handle encoding correctly those csv files are UTF-8, which Microsoft Excel does not create as default. You may reffer to http://stackoverflow.com/questions/4221176/excel-to-csv-with-utf8-encoding for help.

Once you're done editing, create the json file by running ``data_fixture_helper_script_csv_to_json.py``, and replace the old data_fixture.json with the new one.

Another option would be to edit data with the django Admin, and then run:
``python manage.py dumpdata core.Party core.Person core.Facebook_Feed core.Tag --indent 4 > <file_name>.json``

A script to convert the json to the csv files exists as well. Note that currently the file names are hardcoded, so use with caution..
