import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

User = get_user_model()
COUNT_TEST_POSTS: int = 13
COUNT_RECORDS_ON_FIRST_PAGE: int = 10
COUNT_RECORDS_ON_SECOND_PAGE = COUNT_TEST_POSTS - COUNT_RECORDS_ON_FIRST_PAGE
EMPTY: int = 0

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-link',
        )
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
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=PostsPagesTests.author,
            group=PostsPagesTests.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsPagesTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsPagesTests.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsPagesTests.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsPagesTests.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_context(self):
        """Контекст главной страницы соответствует ожидаемому"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIsInstance(
            response.context.get('page_obj'),
            Page,
            'Класс объекта не соответствует ожидаемому'
        )
        self.assertEqual(
            response.context['page_obj'][0].text,
            PostsPagesTests.post.text,
            'Текст поста не соответствует ожидаемому'
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            PostsPagesTests.post.image,
            'Картинка поста не соответствует ожидаемой'
        )

    def test_group_list_page_context(self):
        """Контекст страницы группы соответствует ожидаемому"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsPagesTests.group.slug}
            )
        )
        self.assertIsInstance(
            response.context['group'],
            Group,
            'Класс объекта не соответствует ожидаемому'
        )
        self.assertEqual(
            response.context['page_obj'][0].text,
            PostsPagesTests.post.text,
            'Текст поста не соответствует ожидаемому'
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            PostsPagesTests.post.image,
            'Картинка поста не соответствует ожидаемой'
        )
        values = {
            response.context.get('group').title: PostsPagesTests.group.title,
            response.context.get('group').slug: PostsPagesTests.group.slug,
        }
        for response, field in values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    response,
                    field,
                    'Текст поля не соответствует ожидаемому'
                )

    def test_profile_page_context(self):
        """Контекст страницы профиля соответствует ожидаемому"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostsPagesTests.author}
            )
        )
        self.assertIsInstance(
            response.context['author'],
            User,
            'Класс объекта не соответствует ожидаемому'
        )
        self.assertEqual(
            response.context.get('page_obj')[0].text,
            PostsPagesTests.post.text,
            'Текст поста не соответствует ожидаемому'
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            PostsPagesTests.post.image,
            'Картинка поста не соответствует ожидаемой'
        )

    def test_post_detail_page_context(self):
        """Контекст страницы поста соответствует ожидаемому"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsPagesTests.post.id}
            )
        )
        self.assertIsInstance(
            response.context.get('post'),
            Post,
            'Класс объекта не соответствует ожидаемому'
        )
        self.assertEqual(
            response.context.get('post').image,
            PostsPagesTests.post.image,
            'Картинка поста не соответствует ожидаемой'
        )
        values = {
            response.context.get('post').text: PostsPagesTests.post.text,
            response.context.get('post').group: Group.objects.get(
                title=PostsPagesTests.group.title,
                slug=PostsPagesTests.group.slug,
            ),
            response.context.get('post').author: User.objects.get(
                username=PostsPagesTests.author
            ),
        }
        for response, field in values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    response,
                    field,
                    'Текст поля не соответствует ожидаемому'
                )

    def test_post_edit_page_context(self):
        """Контекст страницы редактирования поста соответствует ожидаемому"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsPagesTests.post.id}
            )
        )
        self.assertIsInstance(
            response.context.get('form'),
            PostForm,
            'Класс объекта не соответствует ожидаемому'
        )
        fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for field, expected in fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(
                    response.context['form'].fields[field],
                    expected,
                    f'Тип поля {field} не соответствует ожидаемому'
                )

    def test_post_create_page_context(self):
        """Контекст страницы создания поста соответствует ожидаемому"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(
            response.context.get('form'),
            PostForm,
            'Класс объекта не соответствует ожидаемому'
        )
        fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for field, expected in fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(
                    response.context['form'].fields[field],
                    expected,
                    f'Тип поля {field} не соответствует ожидаемому'
                )


class PaginationViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-link',
        )
        posts = [
            Post(
                text=f'Текст тестового поста №{number}',
                group=PaginationViewsTests.group,
                author=PaginationViewsTests.author,
            ) for number in range(COUNT_TEST_POSTS)
        ]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest = Client()
        cache.clear()

    def test_pagination_correct(self):
        """Пагинация страниц соответствует ожидаемой"""
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginationViewsTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginationViewsTests.author}
            ),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest.get(page)
                self.assertEqual(
                    len(response.context['page_obj']),
                    COUNT_RECORDS_ON_FIRST_PAGE,
                    f'Количество объектов на первой странице {page} ошибочно',
                )
                response = self.guest.get(page + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    COUNT_RECORDS_ON_SECOND_PAGE,
                    f'Количество объектов на второй странице {page} ошибочно',
                )


class GroupPostTests(TestCase):
    COUNT_RECORDS_ON_PAGE: int = 1

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_not_author')
        cls.author = User.objects.create_user(username='user_author')
        cls.group_correct = Group.objects.create(
            title='Название тестовой группы, содержащей пост',
            slug='group-correct-link',
        )
        cls.group_not_correct = Group.objects.create(
            title='Название тестовой группы, не содержащей пост',
            slug='group-not_correct-link',
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.author,
            group=cls.group_correct
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(GroupPostTests.author)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(GroupPostTests.user)
        cache.clear()

    def test_post_display(self):
        """Пост появляется на нужных страницах"""
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': GroupPostTests.group_correct.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': GroupPostTests.author}
            ),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    response.context['page_obj'].paginator.count,
                    self.COUNT_RECORDS_ON_PAGE,
                    f'Пост не появляется на странице {page}',
                )

    def test_post_not_display_group(self):
        """Пост не появляется на странице не верной группы"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': GroupPostTests.group_not_correct.slug}
            )
        )
        self.assertEqual(
            response.context['page_obj'].paginator.count,
            EMPTY,
            'Пост появляется на странице не верной группы')

    def test_post_not_display_profile(self):
        """Пост не появляется на странице не верного пользователя"""
        response = self.authorized_client_not_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': GroupPostTests.user}
            )
        )
        self.assertEqual(
            response.context['page_obj'].paginator.count,
            EMPTY,
            'Пост появляется на странице не верного пользователя')

    def test_index_page_cache(self):
        """Кеш главной страницы работает корректно"""
        post = Post.objects.create(
            text='Текст тестового поста',
            author=self.author,
        )
        content = self.authorized_client.get(
            reverse('posts:index')
        ).content
        post.delete()
        content_after_delete = self.authorized_client.get(
            reverse('posts:index')
        ).content
        self.assertEqual(
            content,
            content_after_delete,
            'Кеш не сохранился'
        )
        cache.clear()
        cache_clear_content = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(
            content,
            cache_clear_content,
            'Кеш остался после очистки'
        )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.follower = User.objects.create_user(username='follower')
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(FollowTests.author)
        self.follower_client = Client()
        self.follower_client.force_login(FollowTests.follower)
        cache.clear()

    def test_follow(self):
        """Подписка на автора работает корректно"""
        count_followers = Follow.objects.count()
        self.follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.author}
            )
        )
        self.assertEqual(
            Follow.objects.count(),
            count_followers + 1,
            'Новая подписка не создалась'
        )

    def test_unfollow(self):
        """Отписка от автора работает корректно"""
        Follow.objects.create(
            user=FollowTests.follower,
            author=FollowTests.author,
        )
        count_followers = Follow.objects.count()
        self.follower_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowTests.author}
            )
        )
        self.assertEqual(
            Follow.objects.count(),
            count_followers - 1,
            'Подписка не удалилась'
        )

    def test_followers_posts(self):
        """У фолловера отображаются записи тех, на кого он подписан"""
        post = Post.objects.create(
            text='Текст тестового поста',
            author=FollowTests.author,
        )
        Follow.objects.create(
            user=FollowTests.follower,
            author=FollowTests.author,
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertIn(
            post,
            response.context['page_obj'].object_list,
            'Запись не отображается у фолловера'
        )

    def test_unfollowers_posts(self):
        """Запись не отображается у того, кто не подписан"""
        post = Post.objects.create(
            text='Текст тестового поста',
            author=FollowTests.author,
        )

        response = self.author_client.get(reverse('posts:follow_index'))
        self.assertNotIn(
            post,
            response.context['page_obj'].object_list,
            'Запись отображается у того, кто не подписан',
        )
