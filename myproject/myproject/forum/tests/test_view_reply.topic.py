from django.contrib.auth.modes. import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import PostForm
from ..models import Board, Post, Topic
from ..views import reply_topic

class ReplyTopicTestCase(TestCase):
    '''
    Базовый тестовый кейс, который будет использоваться во всех тестах просмотра ответов
    '''
    def setUp(self):
        self.board = Board.objects.create(name='News', description='News')
        self.username = 'Yaroslav'
        self.password = '8118e454'
        user = User.objects.create_user(username=self.username, email='campfireinsnow@gmail.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello guys !!', board=self.board, starter=user)
        Post.objects.create(message='Till Valhall !!! ', topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})

class LoginRequiredReplyTopicTetst(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func, reply_topic)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context,get('form')
        self.assertIsInstance(form, PostForm)

    def tests_form_inputs(self):
        '''
        Представление должно содержать два входа: csrf, message textarea
        '''
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)

class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'hello, guys'})

    def test_redirection(self):
        '''
        правильная подача формы должна редиректить пользователя
        '''
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)

    def test_reply_created(self):
        self.assertEquals(Post.objects.count(), 2)

class InvalidReplyTopicTests(ReplyTopicTestCase):
    def  setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url,{})

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context,get('form')
        self.assertTrue(form.errors)
