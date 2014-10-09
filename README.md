Installation Using Vagrant
========================

Clone the project into your local repository.

Then Copy the file
``kikar_hamedina/kikar_hamedina/local_settings.py.template`` into
``kikar_hamedina/kikar_hamedina/local_settings.py``

Edit it to include your facebook details
- FACEBOOK_SECRET_KEY
- FACEBOOK_APP_ID

Install virtualbox: https://www.virtualbox.org/wiki/Downloads

Install vagrant: https://www.vagrantup.com/downloads.html

cd to kikar_hamedina root directory

Run ``vagrant up`` - this can take about 25-30 minutes

For a successful run you should see something like 'kikar start/running, process 10031' in the end.

This means a virtual machine was successfully created by vagrant (it's an Ubuntu server) and a Django server is running on it on port 8000. The virtual machine and HTTP server are connected to the files on your environment so you can use you favorite text editor to change any project files and these will be reflected on the server (Django will apply changes automatically and reload the server).
You can now access the server from your browser on http://localhost:8000/

Using Vagrant After Installation
===============================

Virtual machine (vagrant) maintenance:

``vagrant destroy`` - destroy virtual machine

``vagrant up`` - create virtual machine or run it if it is down

``vagrant reload --provision`` - re-run the startup script to get the machine and server up and running and apply changes that were made, update data from facebook etc.

``vagrant global-status`` - see status of all machines

``vagrant ssh <id>``  - ssh into machine

After SSH'ing into the machine, you can see the server log in /var/log/upstart/kikar.log (e.g. ``sudo tail -F /var/log/upstart/kikar.log``)


These commands can be used to manage the django server (these are standard Upstart commands):

``sudo stop kikar``

``sudo start kikar``

``sudo restart kikar``

``sudo status kika``


Installation (Deprecated, but might still work)
==============

.. Set the following environment variables:

- DJANGO_SETTINGS_MODULE (for local version set 'kikar_hamedina.settings.local')
- SECRET_KEY
- FACEBOOK_SECRET_KEY
- FACEBOOK_APP_ID

.. Set your db inside ``kikar_hamedina/kikar_hamedina/settings/local.py`` with your db details.

.. Install required packages: ``pip install -r requirements/local.txt --allow-external PIL --allow-unverified PIL`` (for local version requirements)


To Set up DB run the following:

``python manage.py syncdb``
``python manage.py migrate``


This is all very nice, but there's no data :-( To insert initial data
into the db, CTRL-C the server abd run:

``for f in data_fixture_planet data_fixture_mks data_fixture_facebook_feeds 1001_1001 1001_1002 1001_1003 1001_1004 1002_1005 1002_1006 1003_1007 1004_1008; do
	python manage.py loaddata ${f}.json
done``

``python manage.py fetchfeedproperties``

``python manage.py fetchfeedstatuses --initial``

The first command will insert to db data from a pre-created list of parties, persons, feeds, and tags.
The second and third commands will fetch statuses for all feeds in data.
Tag initial sets the request to 1000 messages per feed (as opposed to default of 20), so it might take a while to finish. *Note: Default number of messages is set within fetchfeedstatuses.py command, see file for exact value.


You can also run: ``python manage.py fetchfeedstatuses {feed_id} [--initial]`` to download a single feed.

Once you're all setup run:

``python manage.py runserver``

and enjoy the show.




Editing data_fixture
====================

At the main directory there's a sub-directory called data. Within it there are four csv files, for Party, Person, Feed, and Tag data, which can be edited.

* Note that in order to handle encoding correctly those csv files are UTF-8, which Microsoft Excel does not create as default. You may reffer to http://stackoverflow.com/questions/4221176/excel-to-csv-with-utf8-encoding for help.

Once you're done editing, create the json file by running ``data_fixture_helper_script_csv_to_json.py``, and replace the old data_fixture_facebook_feeds.json with the new one.

Another option would be to edit data with the django Admin, and then run:
``python manage.py dumpdata core.Party core.Person core.Facebook_Feed core.Tag --indent 4 > <file_name>.json``

A script to convert the json to the csv files exists as well. Note that currently the file names are hardcoded, so use with caution..
