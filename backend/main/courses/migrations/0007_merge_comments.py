from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_comments'),
        ('courses', '0006_remove_lessoncontent_gif_and_more'),
    ]

    operations = [
        # This is a merge migration, no operations needed
    ] 