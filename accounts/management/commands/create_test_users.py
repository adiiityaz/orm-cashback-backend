"""
Django management command to create test users:
- Admin (superuser)
- Shopper (regular user)
- Brand (brand user)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from brands.models import Brand

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test users: admin, shopper, and brand'

    def handle(self, *args, **options):
        # Create Admin User
        admin_email = 'admin@ormcashback.com'
        admin_password = 'Admin@123'
        
        if User.objects.filter(email=admin_email).exists():
            self.stdout.write(self.style.WARNING(f'Admin user {admin_email} already exists. Skipping...'))
            admin_user = User.objects.get(email=admin_email)
        else:
            admin_user = User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
                first_name='Admin',
                last_name='User',
                role='USER'  # Admin can have any role
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Admin user created: {admin_email} / {admin_password}'))
        
        # Create Shopper User
        shopper_email = 'shopper@ormcashback.com'
        shopper_password = 'Shopper@123'
        
        if User.objects.filter(email=shopper_email).exists():
            self.stdout.write(self.style.WARNING(f'Shopper user {shopper_email} already exists. Skipping...'))
            shopper_user = User.objects.get(email=shopper_email)
        else:
            shopper_user = User.objects.create_user(
                email=shopper_email,
                password=shopper_password,
                first_name='John',
                last_name='Shopper',
                role='USER',
                phone_number='+1234567890'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Shopper user created: {shopper_email} / {shopper_password}'))
        
        # Create Brand User
        brand_email = 'brand@ormcashback.com'
        brand_password = 'Brand@123'
        
        if User.objects.filter(email=brand_email).exists():
            self.stdout.write(self.style.WARNING(f'Brand user {brand_email} already exists. Skipping...'))
            brand_user = User.objects.get(email=brand_email)
        else:
            brand_user = User.objects.create_user(
                email=brand_email,
                password=brand_password,
                first_name='Brand',
                last_name='Owner',
                role='BRAND',
                phone_number='+1234567891'
            )
            
            # Create Brand Profile
            Brand.objects.get_or_create(
                user=brand_user,
                defaults={
                    'brand_name': 'Test Brand',
                    'description': 'This is a test brand for ORM Cashback Platform',
                    'website': 'https://testbrand.com',
                    'contact_email': brand_email,
                    'contact_phone': '+1234567891',
                    'is_verified': True,
                    'is_active': True,
                    'wallet_balance': 1000.00,
                    'currency': 'USD'
                }
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Brand user created: {brand_email} / {brand_password}'))
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('USER CREDENTIALS SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'\n🔐 ADMIN USER:'))
        self.stdout.write(self.style.SUCCESS(f'   Email: {admin_email}'))
        self.stdout.write(self.style.SUCCESS(f'   Password: {admin_password}'))
        self.stdout.write(self.style.SUCCESS(f'\n🛒 SHOPPER USER:'))
        self.stdout.write(self.style.SUCCESS(f'   Email: {shopper_email}'))
        self.stdout.write(self.style.SUCCESS(f'   Password: {shopper_password}'))
        self.stdout.write(self.style.SUCCESS(f'\n🏢 BRAND USER:'))
        self.stdout.write(self.style.SUCCESS(f'   Email: {brand_email}'))
        self.stdout.write(self.style.SUCCESS(f'   Password: {brand_password}'))
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('\n✅ All users created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nYou can now login using these credentials at:'))
        self.stdout.write(self.style.SUCCESS('   - Admin Panel: http://127.0.0.1:8000/admin/'))
        self.stdout.write(self.style.SUCCESS('   - API Login: http://127.0.0.1:8000/api/auth/login/'))

