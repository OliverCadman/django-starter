from django.test import TestCase
from django.contrib.auth import get_user_model


class UserTests(TestCase):
    """Tests for User Model"""

    def test_create_user(self):
        """Test creating a user successful"""

        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
             email=email, password=password
        )

        self.assertTrue(user.check_password(password))
        self.assertEqual(user.email, email)
    
    def test_normalize_email(self):
        """Test emails are normalized when user created"""

        password = 'testpass123'

        test_emails = [
            ('test1@EXAMPLE.com', 'test1@example.com'),
            ('test2@eXaMpLe.com', 'test2@example.com'),
            ('test3@examplE.com', 'test3@example.com'),
            ('test4@example.COM', 'test4@example.com')
        ]

        for email, expected in test_emails:
            user = get_user_model().objects.create_user(
                 email=email, password=password
            )

            self.assertEqual(user.email, expected)

    def test_create_user_without_username_raises_error(self):
        """Test ValueError raised when user is created without email"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='testpass123'
            )
    
    def test_create_superuser(self):
        """Test creating a superuser is successful"""

        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)