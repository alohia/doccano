# Generated by Django 2.0.5 on 2018-10-30 09:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('text', models.CharField(max_length=65536)),
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now)),
                ('source', models.CharField(default='DS', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prob', models.FloatField(default=0.0)),
                ('manual', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doc_annotations', to='server.Document')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('shortcut', models.CharField(max_length=10)),
                ('background_color', models.CharField(default='#209cee', max_length=7)),
                ('text_color', models.CharField(default='#ffffff', max_length=7)),
                ('documents',
                 models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='doc_labels',
                                   to='server.Document')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500)),
                ('guideline', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project_type', models.CharField(choices=[('DocumentClassification', 'document classification'), ('SequenceLabeling', 'sequence labeling'), ('Seq2seq', 'sequence to sequence')], max_length=30)),
                ('users', models.ManyToManyField(related_name='projects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Seq2seqAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prob', models.FloatField(default=0.0)),
                ('manual', models.BooleanField(default=False)),
                ('text', models.CharField(max_length=5000)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seq2seq_annotations', to='server.Document')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SequenceAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prob', models.FloatField(default=0.0)),
                ('manual', models.BooleanField(default=False)),
                ('start_offset', models.IntegerField()),
                ('end_offset', models.IntegerField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seq_annotations', to='server.Document')),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.Label')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='label',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='server.Project'),
        ),
        migrations.AddField(
            model_name='documentannotation',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.Label'),
        ),
        migrations.AddField(
            model_name='documentannotation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='server.Project'),
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together={('project', 'id')},
        ),
    ]
