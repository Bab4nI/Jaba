from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_add_comment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
    ] 