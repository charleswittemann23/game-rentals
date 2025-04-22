from django import forms
from .models import Game, Comment, Rating, BorrowRequest


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'description', 'release_date', 'genre', 'platform', 'image', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter game title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the game', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Main Library, Shelf A-1'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Action'}),
            'platform': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PC, Xbox'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class RatingForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Rating.RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )

    class Meta:
        model = Rating
        fields = ['rating']


class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['duration_days']
        widgets = {
            'duration_days': forms.Select(attrs={'class': 'form-select'}),
        }
