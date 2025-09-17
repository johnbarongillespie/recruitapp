from django.test import TestCase, Client
from django.urls import reverse

class AgentViewTests(TestCase):
    def setUp(self):
        # This sets up a "client" that can act like a web browser in our tests.
        self.client = Client()

    def test_login_page_loads_correctly(self):
        """
        Tests that the login page returns a successful '200 OK' response.
        """
        # The 'reverse' function finds the URL for our login page by its name.
        response = self.client.get(reverse('login'))
        # We check if the page loaded successfully (status code 200).
        self.assertEqual(response.status_code, 200)

    def test_agent_page_redirects_when_logged_out(self):
        """
        Tests that trying to access the main agent page while not logged in
        results in a redirect (to the login page).
        """
        # The 'reverse' function finds the URL for our agent's main page.
        response = self.client.get(reverse('index'))
        # We check if the response is a redirect (status code 302).
        self.assertEqual(response.status_code, 302)