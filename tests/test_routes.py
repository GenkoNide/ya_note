# news/tests/test_routes.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Метод используется для создания объектов, которые не будут изменяться в течение всех тестов.
        """
        cls.note_mark = Note.objects.create(title='Первые шаги: вроде понимаю',
                                       text='Мы создали двух пользователей, '
                                            'где в строке ниже будем создавать этот пост '
                                            'от имени GenkoNide, используя поля из модели, '
                                            'а от пользователя NotGenkoNide '
                                            'будем проверять на доступность '
                                            'к редактированию, просмотру')
        cls.note = Note.objects.create(
            news=cls.note_mark,
            author=cls.author
        )

    def test_pages_availability_not_auth(self):
        """
        Проверяет доступность не авторизованного пользователя к страницам: главной, регистрации, авторизации и выхода.
        """
        urls = (
            ('notes:home', None),
            ('users:signup', None),
            ('users:login', None),
            ('users:logout', None),
        )
        for path_name, args in urls:
            with self.subTest(name=path_name):
                url = reverse(path_name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_not_auth(self):
        """
        Проверка на редирект не авторизированного пользователя
        на страницу авторизации, со страниц:
        редактирования, информации, удаления заметки
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )
        for path_name, args in urls:
            with self.subTest(name=path_name):
                url = reverse(path_name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_private_pages_availability_not_auth(self):
        url = reverse('notes:detail', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_availability_for_note_edit_and_delete(self):
        """
        Проверка доступности страниц редактирования, удаления, только автору заметки.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(self.user)
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.self,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)


