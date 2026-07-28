import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easyplan.settings')
django.setup()

from django.core.management import call_command
call_command('migrate')
print("Database initialized successfully!")