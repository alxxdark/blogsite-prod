from django import forms
from .models import Comment
from .models import Profile
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Your Message")


MAX_AVATAR_MB = 5

def validate_file_size(f):
    if f and f.size > MAX_AVATAR_MB * 1024 * 1024:
        raise ValidationError(f"Dosya boyutu {MAX_AVATAR_MB} MB'ı geçmemeli.")

class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_file_size],
        help_text="JPG, PNG veya WEBP • max 5 MB"
    )
    # cover alanı eklemek istemezsen forms'tan çıkar; modelinde yoksa ekleme.
    # cover = forms.ImageField(required=False, validators=[...])

    class Meta:
        model = Profile
        fields = ['avatar', 'bio']   # cover kullanıyorsan: ['avatar', 'cover', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Kısa biyografi…'}),
        }