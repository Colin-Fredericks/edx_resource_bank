# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Learning_Objective'
        db.create_table(u'RDB_learning_objective', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('learning_objective', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal(u'RDB', ['Learning_Objective'])

        # Adding model 'Topic'
        db.create_table(u'RDB_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'RDB', ['Topic'])

        # Adding model 'Keyword'
        db.create_table(u'RDB_keyword', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'RDB', ['Keyword'])

        # Adding model 'Code_Dependencies'
        db.create_table(u'RDB_code_dependencies', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codebase', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'RDB', ['Code_Dependencies'])

        # Adding model 'Analytic'
        db.create_table(u'RDB_analytic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'RDB', ['Analytic'])

        # Adding model 'Analytic_Value'
        db.create_table(u'RDB_analytic_value', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['RDB.Analytic'])),
            ('value', self.gf('django.db.models.fields.FloatField')(blank=True)),
        ))
        db.send_create_signal(u'RDB', ['Analytic_Value'])

        # Adding model 'Custom_Text'
        db.create_table(u'RDB_custom_text', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'RDB', ['Custom_Text'])

        # Adding model 'Resource'
        db.create_table(u'RDB_resource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('hide_info', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('resource_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('grade_level', self.gf('django.db.models.fields.CharField')(default='any', max_length=16)),
            ('intended_use', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('license', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('license_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('license_other_notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('analytic_value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['RDB.Analytic_Value'], null=True, blank=True)),
            ('problem_type', self.gf('django.db.models.fields.CharField')(default='not_a_problem', max_length=16)),
        ))
        db.send_create_signal(u'RDB', ['Resource'])

        # Adding M2M table for field learning_objective on 'Resource'
        m2m_table_name = db.shorten_name(u'RDB_resource_learning_objective')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm[u'RDB.resource'], null=False)),
            ('learning_objective', models.ForeignKey(orm[u'RDB.learning_objective'], null=False))
        ))
        db.create_unique(m2m_table_name, ['resource_id', 'learning_objective_id'])

        # Adding M2M table for field keyword on 'Resource'
        m2m_table_name = db.shorten_name(u'RDB_resource_keyword')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm[u'RDB.resource'], null=False)),
            ('keyword', models.ForeignKey(orm[u'RDB.keyword'], null=False))
        ))
        db.create_unique(m2m_table_name, ['resource_id', 'keyword_id'])

        # Adding M2M table for field topic on 'Resource'
        m2m_table_name = db.shorten_name(u'RDB_resource_topic')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm[u'RDB.resource'], null=False)),
            ('topic', models.ForeignKey(orm[u'RDB.topic'], null=False))
        ))
        db.create_unique(m2m_table_name, ['resource_id', 'topic_id'])

        # Adding M2M table for field custom_text on 'Resource'
        m2m_table_name = db.shorten_name(u'RDB_resource_custom_text')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm[u'RDB.resource'], null=False)),
            ('custom_text', models.ForeignKey(orm[u'RDB.custom_text'], null=False))
        ))
        db.create_unique(m2m_table_name, ['resource_id', 'custom_text_id'])

        # Adding M2M table for field analytic on 'Resource'
        m2m_table_name = db.shorten_name(u'RDB_resource_analytic')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm[u'RDB.resource'], null=False)),
            ('analytic', models.ForeignKey(orm[u'RDB.analytic'], null=False))
        ))
        db.create_unique(m2m_table_name, ['resource_id', 'analytic_id'])

        # Adding M2M table for field code_dependencies on 'Resource'
        m2m_table_name = db.shorten_name(u'RDB_resource_code_dependencies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm[u'RDB.resource'], null=False)),
            ('code_dependencies', models.ForeignKey(orm[u'RDB.code_dependencies'], null=False))
        ))
        db.create_unique(m2m_table_name, ['resource_id', 'code_dependencies_id'])

        # Adding model 'Collection'
        db.create_table(u'RDB_collection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('collection_level', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('is_sequential', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'RDB', ['Collection'])


    def backwards(self, orm):
        # Deleting model 'Learning_Objective'
        db.delete_table(u'RDB_learning_objective')

        # Deleting model 'Topic'
        db.delete_table(u'RDB_topic')

        # Deleting model 'Keyword'
        db.delete_table(u'RDB_keyword')

        # Deleting model 'Code_Dependencies'
        db.delete_table(u'RDB_code_dependencies')

        # Deleting model 'Analytic'
        db.delete_table(u'RDB_analytic')

        # Deleting model 'Analytic_Value'
        db.delete_table(u'RDB_analytic_value')

        # Deleting model 'Custom_Text'
        db.delete_table(u'RDB_custom_text')

        # Deleting model 'Resource'
        db.delete_table(u'RDB_resource')

        # Removing M2M table for field learning_objective on 'Resource'
        db.delete_table(db.shorten_name(u'RDB_resource_learning_objective'))

        # Removing M2M table for field keyword on 'Resource'
        db.delete_table(db.shorten_name(u'RDB_resource_keyword'))

        # Removing M2M table for field topic on 'Resource'
        db.delete_table(db.shorten_name(u'RDB_resource_topic'))

        # Removing M2M table for field custom_text on 'Resource'
        db.delete_table(db.shorten_name(u'RDB_resource_custom_text'))

        # Removing M2M table for field analytic on 'Resource'
        db.delete_table(db.shorten_name(u'RDB_resource_analytic'))

        # Removing M2M table for field code_dependencies on 'Resource'
        db.delete_table(db.shorten_name(u'RDB_resource_code_dependencies'))

        # Deleting model 'Collection'
        db.delete_table(u'RDB_collection')


    models = {
        u'RDB.analytic': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Analytic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'RDB.analytic_value': {
            'Meta': {'object_name': 'Analytic_Value'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['RDB.Analytic']"}),
            'value': ('django.db.models.fields.FloatField', [], {'blank': 'True'})
        },
        u'RDB.code_dependencies': {
            'Meta': {'ordering': "('codebase',)", 'object_name': 'Code_Dependencies'},
            'codebase': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'RDB.collection': {
            'Meta': {'object_name': 'Collection'},
            'collection_level': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sequential': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'RDB.custom_text': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Custom_Text'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'RDB.keyword': {
            'Meta': {'ordering': "('keyword',)", 'object_name': 'Keyword'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'RDB.learning_objective': {
            'Meta': {'ordering': "('learning_objective',)", 'object_name': 'Learning_Objective'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'learning_objective': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'RDB.resource': {
            'Meta': {'object_name': 'Resource'},
            'analytic': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['RDB.Analytic']", 'null': 'True', 'blank': 'True'}),
            'analytic_value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['RDB.Analytic_Value']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'code_dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['RDB.Code_Dependencies']", 'symmetrical': 'False', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom_text': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['RDB.Custom_Text']", 'null': 'True', 'blank': 'True'}),
            'grade_level': ('django.db.models.fields.CharField', [], {'default': "'any'", 'max_length': '16'}),
            'hide_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intended_use': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'keyword': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['RDB.Keyword']", 'symmetrical': 'False', 'blank': 'True'}),
            'learning_objective': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['RDB.Learning_Objective']", 'symmetrical': 'False'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'license_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'license_other_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'problem_type': ('django.db.models.fields.CharField', [], {'default': "'not_a_problem'", 'max_length': '16'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'topic': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['RDB.Topic']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'RDB.topic': {
            'Meta': {'ordering': "('topic',)", 'object_name': 'Topic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['RDB']