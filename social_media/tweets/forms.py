from django import forms
from .models import Tweet


class TweetForm(forms.ModelForm):
    """Formulaire pour créer un tweet"""
    
    class Meta:
        model = Tweet
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-x-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-x-blue focus:border-transparent',
                'placeholder': "Quoi de neuf ?",
                'rows': 3,
                'maxlength': 280
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            })
        }
        labels = {
            'content': '',
            'image': ''
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['image'].required = False
