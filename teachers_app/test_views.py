# tests/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

class TeacherDashboardAccessTests(TestCase):
    def setUp(self):
        # Set up client for making requests
        self.client = Client()

        # Create the "Teachers" group
        self.teachers_group = Group.objects.create(name="Teachers")

        # Create a user in the "Teachers" group
        self.teacher_user = User.objects.create_user(username='ekpe', password='password123')
        self.teacher_user.groups.add(self.teachers_group)

        # Create a user not in the "Teachers" group
        self.non_teacher_user = User.objects.create_user(username='student', password='password123')

        # URL for the teacher dashboard view
        self.dashboard_url = reverse('teachers_dashboard')

    def test_teacher_user_access_dashboard(self):
        # Log in as teacher user
        self.client.login(username='teacher', password='password123')
        
        # Access the dashboard
        response = self.client.get(self.dashboard_url)

        # Check that the response contains "Teacher Dashboard"
        self.assertContains(response, "Teachers Dashboard", status_code=200)

    def test_non_teacher_user_access_denied(self):
        # Log in as non-teacher user
        self.client.login(username='student', password='password123')
        
        # Access the dashboard
        response = self.client.get(self.dashboard_url)

        # Check that the response contains "Not allowed here"
        self.assertContains(response, "Not allowed here", status_code=200)

    def test_unauthenticated_user_redirected_to_login(self):
        # Attempt to access the dashboard without logging in
        response = self.client.get(self.dashboard_url)

        # Check that the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))
