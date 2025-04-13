from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from .models import Game
from .forms import GameForm
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
        form = GameForm(data=invalid_data, files=self.game_files)
        self.assertFalse(form.is_valid())
        self.assertIn('release_date', form.errors)
