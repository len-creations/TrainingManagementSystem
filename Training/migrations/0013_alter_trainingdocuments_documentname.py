# Generated by Django 5.1 on 2024-08-27 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Training', '0012_remove_exam_average_marks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingdocuments',
            name='documentname',
            field=models.CharField(max_length=150),
        ),
    ]
