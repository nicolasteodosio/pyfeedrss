# Generated by Django 3.0.8 on 2020-08-05 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0011_auto_20200805_0335"),
    ]

    operations = [
        migrations.AddField(
            model_name="userrelitem",
            name="disabled_at",
            field=models.DateTimeField(null=True, verbose_name="Disabled at"),
        ),
    ]
