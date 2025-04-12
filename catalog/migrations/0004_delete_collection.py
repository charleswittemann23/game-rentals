from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0003_game_created_at_game_platform_game_release_date_and_more'),  # You may need to adjust this to match your actual previous migration
    ]

    operations = [
        migrations.DeleteModel(
            name='Collection',
        ),
    ]