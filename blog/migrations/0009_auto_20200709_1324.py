# Generated by Django 3.0.6 on 2020-07-09 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20200709_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='images',
            name='image',
            field=models.ImageField(blank=True, upload_to='post_images/<built-in function id>'),
        ),
    ]