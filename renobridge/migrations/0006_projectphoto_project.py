# Generated by Django 4.2.16 on 2024-10-29 03:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('renobridge', '0005_remove_project_custom_processes'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectphoto',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='renobridge.project'),
        ),
    ]
