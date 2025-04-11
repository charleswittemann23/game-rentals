from django import forms
from .models import UserProfile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic', 'real_name']

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data['real_name']:
            first_name, last_name = self.cleaned_data['real_name'].split(' ', 1) if ' ' in self.cleaned_data[
                'real_name'] else (self.cleaned_data['real_name'], '')
            user.user.first_name = first_name
            user.user.last_name = last_name
            user.user.save()

        if commit:
            user.save()
        return user
