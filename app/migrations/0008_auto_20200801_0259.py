# Generated by Django 3.0.8 on 2020-08-01 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_auto_20200729_0255"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feed",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Description"),
        ),
    ]