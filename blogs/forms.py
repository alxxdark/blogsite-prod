from django import forms
from .models import Comment
from .models import Profile

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Your Message")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'cover', 'bio']