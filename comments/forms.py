from django import forms
from .models import Comment
from .moderation import moderate_text

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author_name", "text"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.request and self.request.user.is_authenticated and self.request.user.is_superuser:
            obj.is_approved = True
            obj.is_flagged = False
            obj.mod_score = 0.0
            obj.mod_signals = {"bypass": "superuser"}
        else:
            verdict = moderate_text(self.cleaned_data["text"])
            obj.is_approved = verdict["approve"]
            obj.is_flagged  = not verdict["approve"]
            obj.mod_score   = verdict["score"]
            obj.mod_signals = verdict["signals"]

        if commit:
            obj.save()
        return obj
