from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0005_aichatstate"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AIChatState",
        ),
    ]
