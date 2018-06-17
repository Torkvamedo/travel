from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

class PasswordResetMailTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='yarik', email='campfireinsnow@gmail.com', password='123')
        self.response = self.client.post(reverse('password_reset'),{'email':'campfireinsnow@gmail.com'})
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEquals('[Travel4u] Please reset your password', self.email.subject)

    def test_emil_body(self):
        context = self.response.context
        token = context.get('token')
        uid = context.get('uid')
        password_reset_token_url = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn('yarik', self.email.body)
        self.assertIn('campfireinsnow@gmail.com', self.email.body)

    def test_email_to(self):
        self.assertEquals(['campfireinsnow@gmail.com',], self.email.to)
