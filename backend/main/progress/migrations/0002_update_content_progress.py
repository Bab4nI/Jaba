from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contentprogress',
            old_name='last_attempt',
            new_name='updated_at',
        ),
        migrations.AddField(
            model_name='contentprogress',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.DeleteModel(
            name='FormProgress',
        ),
    ] 