from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from notes.models import Note

from notes.forms import NoteForm

User = get_user_model()


class TestHomePage(TestCase):
    HOME_URL = reverse('notes:home')
    COUNT_NOTE = 35

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='GenkoNide')
        all_note_author = [
            Note(title=f'NoteMark {index}',
                 text=f'Заметка № {index}',
                 slug=f'NoteMark_{index}',
                 author=cls.author)
            for index in range(cls.COUNT_NOTE)
        ]
        Note.objects.bulk_create(all_note_author)

    def test_note_count(self):
        """Тест на корректное отображение количества заметок
        на странице заметок пользователся"""
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = len(object_list)
        self.assertEqual(news_count, self.COUNT_NOTE)



class TestDetailPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='GenkoNide')
        cls.user = User.objects.create(username='NotGenkoNide')
        cls.note_author = Note.objects.create(title='NoteMark Author',
                 text='Заметка № 1',
                 slug='NoteMark_Author',
                 author=cls.author)
        cls.note_user = Note.objects.create(title='NoteMark Author',
                 text='Заметка № 1',
                 slug='NoteMark_Author',
                 author=cls.author)
        cls.detail_url = reverse('note:detail', args=(cls.note_author.slug,))

    def test_posts_in_list(self):
        """Тест в котором проверяется что отельная запись передается в object_list на страницу списка записей"""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note_author, object_list)

    def test_not_author_client_has_no_form(self):
        """Тест в котором проверяется запрос анонимного пользователя,
        не передаётся в context словарь автора"""
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_author_client_has_form(self):
        """Тест в котором проверяется запрос автора заметок,
        передаётся в context словарь автора,
        и объект формы соответствует нужному классу формы"""
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_list_not_author_in_list_author(self):
        """Тест в котором проверяется, что в список заметок одного
        пользователя не попадают в список заметок другого пользователя"""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note_user, object_list)

    def test_page_form_in_add_edite(self):
        pages = (
            ('notes:add', None),
            ('notes:edit', {'slug': self.note_author.slug}),
        )
        for page, kwargs in pages:
            with self.subTest(page=page, kwargs=kwargs):
                self.client.force_login(self.author)
                response = self.client.get(self.LIST_URL)
                self.assertIn('form', response.context)
