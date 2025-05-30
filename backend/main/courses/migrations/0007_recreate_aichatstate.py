from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0006_drop_aichatstate"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIChatState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_enabled", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_chat_states",
                        to="courses.lesson",
                    ),
                ),
            ],
            options={
                "verbose_name": "Состояние AI чата",
                "verbose_name_plural": "Состояния AI чата",
            },
        ),
    ]
