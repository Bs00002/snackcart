import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp1.models import User

users = User.objects.filter(role__in=['Customer','Seller']).order_by('id')
with open('readme.txt', 'w', encoding='utf-8') as f:
    f.write('SNACKCART DEMO CREDENTIALS\n')
    f.write('========================\n')
    f.write('Password for all listed users: Example@123\n\n')
    f.write('ID\tName\tEmail\tRole\tStatus\n')
    for u in users:
        f.write(f'{u.id}\t{u.name}\t{u.email}\t{u.role}\t{u.status}\n')

print('readme.txt created with', users.count(), 'users')
