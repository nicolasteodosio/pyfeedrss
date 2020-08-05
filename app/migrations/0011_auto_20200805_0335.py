# Generated by Django 3.0.8 on 2020-08-05 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0010_notification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userrelitem",
            name="kind",
            field=models.CharField(
                choices=[
                    ("comment", "Comment"),
                    ("read", "Read"),
                    ("favorite", "Favorite"),
                    ("unfavorite", "Unfavorite"),
                ],
                max_length=50,
                verbose_name="Kind",
            ),
        ),
    ]
