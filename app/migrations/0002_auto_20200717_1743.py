# Generated by Django 3.0.8 on 2020-07-17 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userfollowfeed",
            name="disabled_at",
            field=models.DateTimeField(null=True, verbose_name="Disabled at"),
        ),
        migrations.DeleteModel(name="UserRelItem",),
    ]
