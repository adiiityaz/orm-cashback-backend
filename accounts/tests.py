from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            role='USER'
        )
        self.assertEqual(user.email, 'user@example.com')
        self.assertEqual(user.role, 'USER')
        self.assertTrue(user.is_user)
        self.assertFalse(user.is_brand)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_brand_user(self):
        """Test creating a brand user"""
        user = User.objects.create_user(
            email='brand@example.com',
            password='testpass123',
            role='BRAND'
        )
        self.assertEqual(user.email, 'brand@example.com')
        self.assertEqual(user.role, 'BRAND')
        self.assertFalse(user.is_user)
        self.assertTrue(user.is_brand)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertIn('test@example.com', str(user))
        self.assertIn('User', str(user))
