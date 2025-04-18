from django import forms
from catalog.models import Game
from .models import Collection, CollectionAccessRequest
from django.core.exceptions import ValidationError


class CollectionForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter collection name'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter collection description'})
    )
    games = forms.ModelMultipleChoiceField(
        queryset=Game.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )

    class Meta:
        model = Collection
        fields = ['name', 'description', 'games', 'is_private']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.userprofile.role == 'Patron':
            self.instance.is_private = False
        else:
            self.fields['is_private'] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )

    def clean_games(self):
        games = self.cleaned_data['games']
        is_private = self.cleaned_data.get('is_private', False)
        
        # Check each game
        for game in games:
            # If the game is in a private collection, it can't be added to any other collection
            if game.is_in_private_collection:
                raise forms.ValidationError(f"Game '{game.title}' is already in a private collection and cannot be added to another collection.")
            
            # If this collection is private and the game is in any other collection, it can't be added
            if is_private and game.collections.exists():
                raise forms.ValidationError(f"Game '{game.title}' is already in another collection and cannot be added to a private collection.")
        
        return games

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Use our custom add_game method for each game
            for game in self.cleaned_data['games']:
                try:
                    instance.add_game(game)
                except ValidationError as e:
                    raise forms.ValidationError(str(e))
        return instance

class CollectionAccessRequestForm(forms.ModelForm):
    class Meta:
        model = CollectionAccessRequest
        fields = ['collection', 'requester']
        widgets = {
            'collection': forms.HiddenInput(),
            'requester': forms.HiddenInput(),
        }
