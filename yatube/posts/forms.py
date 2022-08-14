from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_text(self):
        text_form = self.cleaned_data['text']
        if text_form == '' or text_form.isspace():
            raise forms.ValidationError('Поле текст не может быть пустым!')
        return text_form
