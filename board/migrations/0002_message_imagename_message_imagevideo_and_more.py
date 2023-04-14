# Generated by Django 4.1.7 on 2023-04-14 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='imageName',
            field=models.CharField(default='image', max_length=15),
        ),
        migrations.AddField(
            model_name='message',
            name='imageVideo',
            field=models.CharField(default='video', max_length=15),
        ),
        migrations.AlterField(
            model_name='message',
            name='messageImage',
            field=models.ImageField(blank=True, null=True, upload_to='images/', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='message',
            name='messageVideo',
            field=models.FileField(blank=True, null=True, upload_to='videos/', verbose_name=''),
        ),
    ]