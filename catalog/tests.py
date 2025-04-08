from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from .models import Game, Collection
from .forms import GameForm, CollectionForm
from django.core.files.uploadedfile import SimpleUploadedFile

class GameFormTest(TestCase):
    def setUp(self):
        small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
        
        self.test_image= SimpleUploadedFile(name='test.gif',content=small_gif, content_type='image/gif')
        # Create test data that we'll need
        self.game_data = {
            'title': 'Test Game',
            'description': 'A game for testing purposes',
            'release_date': date(2023, 1, 1),
            'genre': 'Action',
            'platform': 'PC',
             
        }
        self.game_files = {
        'image': self.test_image
    }
        
    def test_game_form_valid_data(self):
        form = GameForm(data=self.game_data, files=self.game_files)
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        self.assertTrue(form.is_valid())
    
    def test_game_form_empty_data(self):
        form = GameForm(data={})
        self.assertFalse(form.is_valid())
        # Check that required fields are flagged
        self.assertIn('title', form.errors)
        self.assertIn('description', form.errors)
        # Add other required fields as needed
        
    def test_game_form_invalid_date(self):
        invalid_data = self.game_data.copy()
        invalid_data['release_date'] = 'not-a-date'
        form = GameForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('release_date', form.errors)


class CollectionFormTest(TestCase):
    def setUp(self):
        # Create a test user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='testpass123'
        )
        
        # Create a patron user (assuming this is set in the user profile)
        self.patron_user = User.objects.create_user(
            username='patron_user',
            password='testpass123'
        )
        # Set up the profile for patron user
        profile = self.patron_user.userprofile
        profile.role = 'Patron'
        profile.save()
        
        # Create test games
        self.game1 = Game.objects.create(
            title='Game 1',
            description='Description 1',
            release_date=date(2023, 1, 1),
            genre='Action',
            platform='PC'
        )
        
        self.game2 = Game.objects.create(
            title='Game 2',
            description='Description 2',
            release_date=date(2023, 2, 2),
            genre='RPG',
            platform='Console'
        )
        
        # Valid collection data
        self.collection_data = {
            'name': 'Test Collection',
            'description': 'A collection for testing',
            'games': [self.game1.id, self.game2.id],
            'is_private': True
        }
    
    def test_collection_form_valid_data(self):
        form = CollectionForm(data=self.collection_data, user=self.regular_user)
        self.assertTrue(form.is_valid())
    
    def test_collection_form_empty_data(self):
        form = CollectionForm(data={}, user=self.regular_user)
        self.assertFalse(form.is_valid())
        # Check that required fields are flagged
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('games', form.errors)
    
    
    
    def test_regular_user_can_set_private(self):
        # Regular users should be able to set is_private
        form = CollectionForm(data=self.collection_data, user=self.regular_user)
        self.assertTrue(form.is_valid())
        
        collection = form.save(commit=False)
        # Set the creator field
        collection.creator = self.regular_user
        # Now save the model
        collection.save()
        # Save the many-to-many data
        form.save_m2m()
        self.assertTrue(collection.is_private)
        
        # Verify the is_private field is available for regular users
        self.assertIn('is_private', form.fields)
    
    def test_form_validation_with_no_games(self):
        invalid_data = self.collection_data.copy()
        invalid_data['games'] = []
        form = CollectionForm(data=invalid_data, user=self.regular_user)
        self.assertFalse(form.is_valid())
        self.assertIn('games', form.errors)