from django import forms
from catalog.models import Game
from .models import Collection, CollectionAccessRequest


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

        # Make collection public by default for 'Patron' users
        userprofile = getattr(self.user, 'userprofile', None)
        if userprofile and userprofile.role == 'Patron':
            self.instance.is_private = False
        else:
            self.fields['is_private'] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )

        # Filter out games that are in private collections except the current
        private_games = Game.objects.filter(collections__is_private=True).exclude(collections=self.instance).distinct()
        self.fields['games'].queryset = self.fields['games'].queryset.exclude(id__in=private_games)

    def clean_games(self):
        games = self.cleaned_data['games']
        collection = self.instance

        for game in games:
            # If the game is in a private collection, it cannot be added to any other collection
            if game.collections.filter(is_private=True).exclude(id=collection.id).exists():
                raise forms.ValidationError(f"Game '{game.title}' is already in a private collection and cannot be "
                                            f"added to another collection.")

        return games

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            instance.games.set(self.cleaned_data['games'])

            if instance.is_private and instance.pk:
                for game in instance.games.all():
                    for collection in game.collections.exclude(id=instance.id):
                        collection.games.remove(game)
        return instance


class CollectionAccessRequestForm(forms.ModelForm):
    class Meta:
        model = CollectionAccessRequest
        fields = ['collection', 'requester']
        widgets = {
            'collection': forms.HiddenInput(),
            'requester': forms.HiddenInput(),
        }
