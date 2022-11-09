from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': 'Введите текст поста:',
            'group': 'Укажите подходящую группу:',
        }
        help_texts = {
            'group': 'Можете указать тематику поста или оставить поле пустым'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
