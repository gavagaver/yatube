from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group, Comment, TITLE_CHAR_COUNT

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
        )
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test_group_slug',
            description='Описание тестовой группы.',
        )

    def test_models_str_is_correct(self):
        """__str__ модели соответствует ожидаемому."""
        post = PostModelTest.post
        self.assertEqual(
            post.text[:TITLE_CHAR_COUNT] + '...',
            str(post),
            '__str__ модели Post не совпадает с ожидаемым',
        )
        group = PostModelTest.group
        self.assertEqual(
            group.title,
            str(group),
            '__str__ модели Group не совпадает с ожидаемым',
        )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
        )
        cls.comment = Comment.objects.create(
            text='Текст тестового комментария',
            author=cls.user,
            post=cls.post,
        )

    def test_comment_str_is_correct(self):
        """__str__ модели соответствует ожидаемому."""
        comment = CommentModelTest.comment
        self.assertEqual(
            comment.text[:TITLE_CHAR_COUNT] + '...',
            str(comment),
            '__str__ модели Comment не совпадает с ожидаемым',
        )
