# Generated by Django 3.0.6 on 2020-07-17 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_commentrating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentrating',
            name='comment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='comment_rating', to='blog.Comment'),
        ),
    ]