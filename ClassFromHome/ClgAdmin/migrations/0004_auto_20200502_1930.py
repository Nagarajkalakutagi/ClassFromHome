# Generated by Django 3.0.5 on 2020-05-02 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ClgAdmin', '0003_auto_20200428_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment_submit',
            name='assign_accept',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assignment_submit',
            name='assign_comment',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='assignment_submit',
            name='assign_reject',
            field=models.BooleanField(default=False),
        ),
    ]
