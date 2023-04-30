from http import HTTPStatus

from django.test import TestCase


class CoreUrlTests(TestCase):
    def test_page_not_found(self):
        response = self.client.get('/page_not_found/')
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND,
            'Статус-код ответа не соответствует ожидаемому'
        )
        self.assertTemplateUsed(
            response,
            'core/404.html',
            'Шаблон ответа не соответствует ожидаемому'
        )
