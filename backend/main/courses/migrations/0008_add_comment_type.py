from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_merge_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_type',
            field=models.CharField(
                choices=[('COMMENT', 'Комментарий'), ('SOLUTION', 'Решение')],
                default='COMMENT',
                max_length=20
            ),
        ),
    ] 