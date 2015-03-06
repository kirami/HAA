# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Item.record_number_two'
        db.add_column(u'audio_item', 'record_number_two',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Item.record_number_two'
        db.delete_column(u'audio_item', 'record_number_two')


    models = {
        u'audio.address': {
            'Meta': {'object_name': 'Address'},
            'address_one': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'address_three': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'address_two': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'audio.auction': {
            'Meta': {'object_name': 'Auction'},
            'blind_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'flat_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'second_chance_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'second_chance_start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'audio.bid': {
            'Meta': {'unique_together': "(('user', 'item'),)", 'object_name': 'Bid'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '2.0', 'max_digits': '19', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Invoice']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bidItem'", 'to': u"orm['audio.Item']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bidUser'", 'to': u"orm['auth.User']"}),
            'winner': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'audio.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_bid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'audio.condition': {
            'Meta': {'object_name': 'Condition'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Auction']"}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'audio.consignment': {
            'Meta': {'unique_together': "(('minimum', 'item'), ('maximum', 'item'))", 'object_name': 'Consignment'},
            'consignor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'consignmentConsignor'", 'to': u"orm['audio.Consignor']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'consignedItem'", 'to': u"orm['audio.Item']"}),
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
            'discount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '19', 'decimal_places': '2'}),
            'discount_percent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '19', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {}),
            'invoiced_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'on_hold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reminder_invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'second_chance_invoice_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '19', 'decimal_places': '2'}),
            'second_chance_invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'second_chance_shipping': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '19', 'decimal_places': '2'}),
            'second_chance_tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '19', 'decimal_places': '2'}),
            'shipped_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '19', 'decimal_places': '2'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '19', 'decimal_places': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'userInvoice'", 'to': u"orm['auth.User']"})
        },
        u'audio.item': {
            'Meta': {'unique_together': "(('auction', 'lot_id'),)", 'object_name': 'Item'},
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'artist_two': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Auction']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'itemCategory'", 'to': u"orm['audio.Category']"}),
            'condition': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'defect': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'item_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'itemType'", 'to': u"orm['audio.ItemType']"}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audio.Label']", 'null': 'True'}),
            'lot_id': ('django.db.models.fields.IntegerField', [], {'default': "' '", 'null': 'True', 'blank': 'True'}),
            'min_bid': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'name_two': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'record_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'record_number_two': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'audio.itemtype': {
            'Meta': {'object_name': 'ItemType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
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
            'date_received': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'paymentInvoice'", 'to': u"orm['audio.Invoice']"}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'paymentUser'", 'to': u"orm['auth.User']"})
        },
        u'audio.printedcatalog': {
            'Meta': {'object_name': 'PrintedCatalog'},
            'auction': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pcUser'", 'to': u"orm['auth.User']"})
        },
        u'audio.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'billing_address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'upBilling'", 'to': u"orm['audio.Address']"}),
            'confirmation_code': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'courtesy_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deadbeat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ebay': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'pdf_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quiet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shipping_address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'upShipping'", 'to': u"orm['audio.Address']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'upUser'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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