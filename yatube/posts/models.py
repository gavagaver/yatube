from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import CreatedModel

User = get_user_model()
TITLE_CHAR_COUNT: int = 15


class Group(models.Model):
    """
    Модель группы.

    :param title: Название группы.
    :param slug: Уникальный идентификатор группы.
    :param description: Описание группы.
    """
    title = models.CharField(verbose_name='Название', max_length=200)
    slug = models.SlugField(verbose_name='Линк', unique=True)
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        """
        Возвращает строковое представление модели.

        :return: Название группы.
        """
        return f'{self.title}'


class Like(models.Model):
    """
    Модель лайка пользователем поста.

    :param user: Пользователь, который поставил лайк под постом.
    :param content_type:
    :param object_id:
    :param content_object:
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пользователь',
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id',
    )

    def __str__(self):
        return (
            f'{self.user} лайкнул '
            f'{self.content_type} {self.object_id} "{self.content_object}"'
        )


class Post(models.Model):
    """
    Модель поста.

    :param text: Текст поста.
    :param pub_date: Дата и время публикации.
    :param author: Автор поста.
    :param group: Группа, к которой относится пост.
    :param image: Изображение, прикрепленное к посту.
    """
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )
    likes = GenericRelation(Like)

    def __str__(self):
        """
        Возвращает строковое представление модели.

        :return: Текст поста.
        """
        return f'{self.text[:TITLE_CHAR_COUNT] + "..."}'

    class Meta:
        ordering = ('-pub_date',)

    @property
    def total_likes(self):
        return self.likes.count()


class Comment(CreatedModel):
    """
    Модель комментария.

    :param post: Пост, к которому оставлен комментарий.
    :param author: Автор комментария.
    :param text: Текст комментария.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст нового комментария',
    )

    def __str__(self):
        """
        Возвращает строковое представление модели.

        :return: Текст комментария.
        """
        return f'{self.text[:TITLE_CHAR_COUNT] + "..."}'


class Follow(models.Model):
    """
    Модель подписки пользователя на автора.

    :param user: Пользователь, который подписывается на автора.
    :param author: Автор, на которого подписывается пользователь.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
