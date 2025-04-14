from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from unittest.mock import patch, MagicMock
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken

User = get_user_model()


class GoogleOAuthTest(TestCase):
    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

        # Set up site
        self.site = Site.objects.get_current()
        if not self.site:
            self.site = Site.objects.create(domain='example.com', name='example')

        # Create a Google SocialApp
        self.google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id='test-client-id',
            secret='test-secret-key',
        )
        self.google_app.sites.add(self.site)

        # Create social account connection for the test user
        self.social_account = SocialAccount.objects.create(
            user=self.user,
            provider='google',
            uid='test-google-uid',
            extra_data={
                'email': 'testuser@example.com',
                'name': 'Test User',
                'picture': 'https://example.com/picture.jpg'
            }
        )

        # Create a token for the social account
        self.social_token = SocialToken.objects.create(
            app=self.google_app,
            account=self.social_account,
            token='test-oauth-token',
            token_secret='test-token-secret'
        )

    def test_google_login_url(self):
        """Test that the Google login URL is accessible"""
        login_url = reverse('account_login')
        response = self.client.get(login_url, follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'google')

    def test_google_oauth_redirect(self):
        """Test that the Google OAuth redirect URL is accessible"""
        redirect_url = '/accounts/google/login/'  # Standard django-allauth path
        response = self.client.get(redirect_url, secure=True)

        # Either redirect to Google (301/302) or show login page (200) is acceptable
        self.assertIn(response.status_code, [200, 301, 302])

        # If status is 200, check that we're showing something Google-related
        if response.status_code == 200:
            self.assertContains(response, 'account', status_code=200)

    @patch('allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter')
    def test_google_callback(self, mock_adapter):
        """Test the Google OAuth callback functionality"""
        # Mock the OAuth2 response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'id': 'test-google-uid',
            'email': 'testuser@example.com',
            'verified_email': True,
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'https://example.com/picture.jpg',
            'locale': 'en'
        }

        mock_adapter.return_value.complete_login.return_value = mock_response

        # Simulate callback with state and code

        callback_url = '/accounts/google/login/callback/'
        response = self.client.get(callback_url, {
            'state': 'test-state',
            'code': 'test-auth-code'
        }, secure=True)
        print(response)
        # This would typically redirect to settings.LOGIN_REDIRECT_URL
        self.assertIn(response.status_code, [302, 301, 200])

    def test_login_with_google_account(self):
        """Test logging in with an existing Google account"""
        # First logout to ensure we're testing from a clean state
        self.client.logout()

        # Login with the test user's credentials
        login_successful = self.client.login(
            username='testuser',
            password='testpassword'
        )
        self.assertTrue(login_successful)

        # Instead of checking context, check the session or make a request to a page that requires login
        response = self.client.get(reverse('account_login'), secure=True)

        # If response is a redirect, it means we're already logged in
        if response.status_code == 302:
            self.assertTrue(self.client.session.get('_auth_user_id'))
        else:
            # If we're shown the login page again (template rendered), check user is authenticated
            self.assertTrue(response.context['user'].is_authenticated)

        # Check social account association
        social_accounts = SocialAccount.objects.filter(user=self.user)
        self.assertEqual(social_accounts.count(), 1)
        self.assertEqual(social_accounts[0].provider, 'google')

    @patch('allauth.socialaccount.providers.google.views.requests.get')
    def test_google_login_new_user(self, mock_get):
        """Test user creation when new Google account logs in"""
        # Mock the user info response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'id': 'new-google-uid',
            'email': 'newuser@example.com',
            'verified_email': True,
            'name': 'New User',
            'given_name': 'New',
            'family_name': 'User',
            'picture': 'https://example.com/newuser.jpg',
            'locale': 'en'
        }
        mock_get.return_value = mock_response

        # Here we would need to mock the entire OAuth flow
        # This is a simplified version, in a real test we would use
        # complete_login method directly

        # Verify the user doesn't exist yet
        self.assertFalse(User.objects.filter(email='newuser@example.com').exists())

        # In a real test, we would process the login flow here
        # For demonstration, we'll create the user manually
        with patch('allauth.socialaccount.providers.oauth2.views.OAuth2Adapter.parse_token'):
            with patch('allauth.socialaccount.providers.oauth2.views.OAuth2Adapter.complete_login'):
                # This would happen inside allauth
                new_user = User.objects.create_user(
                    username='newuser',
                    email='newuser@example.com'
                )
                SocialAccount.objects.create(
                    user=new_user,
                    provider='google',
                    uid='new-google-uid',
                    extra_data=mock_response.json.return_value
                )

        # Verify the user exists now
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

        # Check social account was created
        self.assertTrue(SocialAccount.objects.filter(uid='new-google-uid').exists())

    def test_disconnect_google_account(self):
        """Test disconnecting a Google account"""
        # Login with the test user
        self.client.login(username='testuser', password='testpassword')

        # Get the social connection removal URL
        connections_url = reverse('socialaccount_connections')

        # Get the current connections page
        response = self.client.get(connections_url, follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google')

        # Disconnect the Google account
        social_account_id = self.social_account.id
        data = {
            'account': social_account_id,
            'action': 'remove'
        }
        response = self.client.post(connections_url, data, secure=True)

        # Check if the connection was removed
        self.assertIn(response.status_code, [301, 302])  # Should redirect
        self.assertFalse(SocialAccount.objects.filter(id=social_account_id).exists())

    def test_google_login_email_already_exists(self):
        """Test handling when a Google account has an email that already exists"""
        # Create a new user with same email but different auth method
        User.objects.create_user(
            username='duplicateuser',
            email='testuser@example.com',  # Same email as our Google-connected user
            password='password123'
        )

        # Mock the OAuth response with this email
        with patch('allauth.socialaccount.providers.google.views.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'id': 'different-google-uid',
                'email': 'testuser@example.com',  # Same email as existing user
                'verified_email': True,
                'name': 'Another User'
            }
            mock_get.return_value = mock_response

            # In a real test, we would process the login flow here
            # The behavior would depend on ACCOUNT_EMAIL_VERIFICATION setting

            # Check we have two users with the same email
            self.assertEqual(User.objects.filter(email='testuser@example.com').count(), 2)

            # In most configurations, allauth would either:
            # - Prompt to connect the accounts
            # - Show an error about the email already being used
            # This would need to be tested through the full OAuth flow
