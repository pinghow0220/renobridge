# Generated by Django 4.2.16 on 2024-10-28 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('renobridge', '0002_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(default='In Progress', max_length=20),
        ),
    ]
