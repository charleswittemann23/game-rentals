from django import forms
from .models import Game, Comment, Rating


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'description', 'genre', 'platform', 'location', 'image']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Main Library, Shelf A-1'}),
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
