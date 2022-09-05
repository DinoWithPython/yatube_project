from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Текст комментария',
        }

    def clean_text(self):
        text_form = self.cleaned_data['text']
        if text_form == 'азазазаз!!!1!1!':
            raise forms.ValidationError('Поздравляем, Вы тролль! :)')
        elif text_form.isspace():
            raise forms.ValidationError('Пробелы - зло')
        return text_form
