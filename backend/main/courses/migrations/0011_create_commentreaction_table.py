from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0010_merge_20250510_1844'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction_type', models.CharField(choices=[('LIKE', 'Нравится'), ('DISLIKE', 'Не нравится')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='courses.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_reactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Реакция на комментарий',
                'verbose_name_plural': 'Реакции на комментарии',
                'unique_together': {('comment', 'user')},
            },
        ),
    ] 