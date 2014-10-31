# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Auction'
        db.create_table(u'audio_auction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('second_chance_end_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('flat_bid_amount', self.gf('django.db.models.fields.DecimalField')(default=2.0, max_digits=19, decimal_places=2)),
        ))
        db.send_create_signal(u'audio', ['Auction'])

        # Adding model 'Invoice'
        db.create_table(u'audio_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Auction'])),
            ('invoiced_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('invoice_date', self.gf('django.db.models.fields.DateField')()),
            ('reminder_invoice_date', self.gf('django.db.models.fields.DateField')()),
            ('second_chance_invoice_amount', self.gf('django.db.models.fields.DateField')()),
            ('second_chance_invoice_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'audio', ['Invoice'])

        # Adding model 'Payment'
        db.create_table(u'audio_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('payment_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Invoice'])),
            ('received_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'audio', ['Payment'])

        # Adding model 'Category'
        db.create_table(u'audio_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'audio', ['Category'])

        # Adding model 'Label'
        db.create_table(u'audio_label', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parent', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'audio', ['Label'])

        # Adding model 'Item'
        db.create_table(u'audio_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Label'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('record_number', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('min_bid', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('lot_id', self.gf('django.db.models.fields.IntegerField')(default=' ', null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Category'])),
            ('condition', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Auction'])),
        ))
        db.send_create_signal(u'audio', ['Item'])

        # Adding unique constraint on 'Item', fields ['auction', 'lot_id']
        db.create_unique(u'audio_item', ['auction_id', 'lot_id'])

        # Adding model 'Bid'
        db.create_table(u'audio_bid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Item'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=2.0, max_digits=19, decimal_places=2)),
            ('winner', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'audio', ['Bid'])

        # Adding unique constraint on 'Bid', fields ['user', 'item']
        db.create_unique(u'audio_bid', ['user_id', 'item_id'])

        # Adding model 'UserProfile'
        db.create_table(u'audio_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('pdf_list', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('printed_list', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('courtesy_list', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deadbeat', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'audio', ['UserProfile'])

        # Adding model 'Address'
        db.create_table(u'audio_address', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('address_one', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('address_two', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('country', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('cell_phone', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal(u'audio', ['Address'])

        # Adding model 'Consignor'
        db.create_table(u'audio_consignor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Address'], null=True, blank=True)),
        ))
        db.send_create_signal(u'audio', ['Consignor'])

        # Adding model 'Consignment'
        db.create_table(u'audio_consignment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Item'])),
            ('consignor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audio.Consignor'])),
            ('percentage', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('minimum', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('maximum', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'audio', ['Consignment'])


    def backwards(self, orm):
        # Removing unique constraint on 'Bid', fields ['user', 'item']
        db.delete_unique(u'audio_bid', ['user_id', 'item_id'])

        # Removing unique constraint on 'Item', fields ['auction', 'lot_id']
        db.delete_unique(u'audio_item', ['auction_id', 'lot_id'])

        # Deleting model 'Auction'
        db.delete_table(u'audio_auction')

        # Deleting model 'Invoice'
        db.delete_table(u'audio_invoice')

        # Deleting model 'Payment'
        db.delete_table(u'audio_payment')

        # Deleting model 'Category'
        db.delete_table(u'audio_category')

        # Deleting model 'Label'
        db.delete_table(u'audio_label')

        # Deleting model 'Item'
        db.delete_table(u'audio_item')

        # Deleting model 'Bid'
        db.delete_table(u'audio_bid')

        # Deleting model 'UserProfile'
        db.delete_table(u'audio_userprofile')

        # Deleting model 'Address'
        db.delete_table(u'audio_address')

        # Deleting model 'Consignor'
        db.delete_table(u'audio_consignor')

        # Deleting model 'Consignment'
        db.delete_table(u'audio_consignment')


    models = {
        u'audio.address': {
            'Meta': {'object_name': 'Address'},
            'address_one': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'address_two': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'cell_phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        u'audio.auction': {
            'Meta': {'object_name': 'Auction'},
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'flat_bid_amount': ('django.db.models.fields.DecimalField', [], {'default': '2.0', 'max_digits': '19', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'second_chance_end_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'audio.bid': {
            'Meta': {'unique_together': "(('user', 'item'),)", 'object_name': 'Bid'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '2.0', 'max_digits': '19', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Item']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'winner': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'audio.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'audio.consignment': {
            'Meta': {'object_name': 'Consignment'},
            'consignor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Consignor']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Item']"}),
            'maximum': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'minimum': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'})
        },
        u'audio.consignor': {
            'Meta': {'object_name': 'Consignor'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Address']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'audio.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Auction']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {}),
            'invoiced_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'reminder_invoice_date': ('django.db.models.fields.DateField', [], {}),
            'second_chance_invoice_amount': ('django.db.models.fields.DateField', [], {}),
            'second_chance_invoice_date': ('django.db.models.fields.DateField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'audio.item': {
            'Meta': {'unique_together': "(('auction', 'lot_id'),)", 'object_name': 'Item'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Auction']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Category']"}),
            'condition': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Label']", 'null': 'True'}),
            'lot_id': ('django.db.models.fields.IntegerField', [], {'default': "' '", 'null': 'True', 'blank': 'True'}),
            'min_bid': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'record_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'audio.label': {
            'Meta': {'object_name': 'Label'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'audio.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Invoice']"}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'received_date': ('django.db.models.fields.DateField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'audio.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'courtesy_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deadbeat': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pdf_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'printed_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['audio']