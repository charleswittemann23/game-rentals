from django import forms
from catalog.models import Game
from .models import Collection


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
