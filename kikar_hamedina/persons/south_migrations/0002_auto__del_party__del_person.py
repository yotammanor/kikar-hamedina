# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Party'
        db.delete_table(u'persons_party')

        # Deleting model 'Person'
        db.delete_table(u'persons_person')


    def backwards(self, orm):
        # Adding model 'Party'
        db.create_table(u'persons_party', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal(u'persons', ['Party'])

        # Adding model 'Person'
        db.create_table(u'persons_person', (
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(related_name='persons', to=orm['persons.Party'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal(u'persons', ['Person'])


    models = {
        
    }

    complete_apps = ['persons']