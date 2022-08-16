from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }

    def clean_text(self):
        text_form = self.cleaned_data['text']
        if text_form == 'yandex':
            raise forms.ValidationError('Вы нашли пасхалку! :)')
        elif text_form.isspace():
            raise forms.ValidationError('Пробелы - зло')
        return text_form
