import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

CURRENT_TEXT = 'Текущий текст поста'
NEW_TEXT = 'Новый текст поста'
EMPTY = 0


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='user_author')
        cls.com_author = User.objects.create_user(username='com_author')
        cls.current_group = Group.objects.create(
            title='Текущая группа',
            slug='current-group-link',
            description='Описание текущей группы'
        )
        cls.new_group = Group.objects.create(
            title='Новая группа',
            slug='new-group-link',
            description='Описание новой группы'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.author)
        self.authorized_client_com = Client()
        self.authorized_client_com.force_login(PostFormTests.com_author)

    def test_post_create(self):
        """Пост создается корректно"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': CURRENT_TEXT,
            'group': PostFormTests.current_group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.author}),
            msg_prefix='Редирект не соответствует ожидаемому'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Новый пост не появился в списке постов'
        )
        created_post = Post.objects.latest('pub_date')
        self.assertEqual(
            created_post.author,
            self.author,
            'Автор не соответствует ожидаемому'
        )
        self.assertEqual(
            created_post.text,
            CURRENT_TEXT,
            'Текст не соответствует ожидаемому'
        )
        self.assertEqual(
            created_post.group,
            PostFormTests.current_group,
            'Группа не соответствует ожидаемой'
        )
        self.assertEqual(
            created_post.image.name,
            'posts/small.gif',
            'Картинка не соответствует ожидаемой'
        )
        self.assertTrue(
            Post.objects.filter(
                id=created_post.id,
                text=created_post.text,
                image=created_post.image,
            ).exists()
        )

    def test_post_edit(self):
        """Пост редактируется корректно"""
        current_form_data = {
            'text': CURRENT_TEXT,
            'group': PostFormTests.current_group.id,
        }
        new_form_data = {
            'text': NEW_TEXT,
            'group': PostFormTests.new_group.id,
        }
        post = self.authorized_client.post(
            reverse('posts:post_create'),
            data=current_form_data,
            follow=True
        )
        posts_count = Post.objects.count()
        post = Post.objects.latest('pub_date')
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=new_form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id}),
            msg_prefix='Редирект не соответствует ожидаемому'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Количество постов не соответствует ожидаемому'
        )
        self.assertTrue(
            Post.objects.filter(
                text=NEW_TEXT,
                group=PostFormTests.new_group
            ).exists(),
            'Отредактированный пост не соответствует ожидаемому'
        )
        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.current_group.slug,))
        )
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count,
            EMPTY,
            'Пост не исчез со страницы старой группы',
        )
        new_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.new_group.slug,))
        )
        self.assertNotEqual(
            new_group_response.context['page_obj'].paginator.count,
            EMPTY,
            'Пост не появился на странице новой группы',
        )

    def test_add_comment(self):
        """Комментарий добавляется корректно"""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='Текст тестового поста',
            author=self.author,
        )
        form_data = {'text': 'Текст тестового комментария'}
        self.authorized_client_com.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.latest('created')
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            'Новый комментарий не появился в списке комментариев'
        )
        self.assertEqual(
            comment.text,
            form_data['text'],
            'Текст не соответствует ожидаемому',
        )
        self.assertEqual(
            comment.author,
            self.com_author,
            'Автор не соответствует ожидаемому',
        )
