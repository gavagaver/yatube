from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostsURLsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_not_author')
        cls.author = User.objects.create_user(username='user_author')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-link',
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=PostsURLsTests.author,
            group=PostsURLsTests.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLsTests.author)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(PostsURLsTests.user)

    def test_urls_access_for_guest(self):
        """Страницы доступны гостю."""
        public_urls = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLsTests.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLsTests.author}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLsTests.post.id}
            ): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, status_code in public_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    status_code,
                    f'Работа страницы {url} не совпадает с ожидаемой',
                )

        response = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLsTests.post.id}
            ),
        )
        self.assertNotEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница редактирования поста доступна гостю',
        )

    def test_urls_access_for_user(self):
        """Страницы доступны авторизованному пользователю."""
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLsTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLsTests.author}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLsTests.post.id}
            ),
            '/create/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client_not_author.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Работа страницы {url} не совпадает с ожидаемой',
                )

        response = self.authorized_client_not_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLsTests.post.id}
            )
        )
        self.assertNotEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница редактирования поста доступна пользователю не автору',
        )

    def test_urls_access_for_author(self):
        """Страницы доступны автору."""
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLsTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLsTests.author}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLsTests.post.id}
            ),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLsTests.post.id}
            ),
            '/create/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Работа страницы {url} не совпадает с ожидаемой',
                )

    def test_urls_redirect_guest_on_admin_login(self):
        """Страница перенаправит гостя на страницу логина."""
        urls = (
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLsTests.post.id}
            ),
            '/create/',
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}',
                )

    def test_urls_redirect_not_author_on_post(self):
        """Страница перенаправит пользователя не автора на страницу поста.
        """
        urls = (
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLsTests.post.id}
            ),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client_not_author.get(
                    url,
                    follow=True
                )
                self.assertRedirects(
                    response,
                    reverse(
                        'posts:post_detail',
                        kwargs={'post_id': PostsURLsTests.post.id}
                    ),
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostsURLsTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostsURLsTests.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLsTests.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsURLsTests.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
