import unittest
import sys
import os

# Add the src directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, startup_banner

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Course Explainer', response.data)
        # Test that course names are displayed
        self.assertIn(b'Introduction to Python', response.data)
        self.assertIn(b'Web Development with Flask', response.data)
        self.assertIn(b'Data Science Fundamentals', response.data)
        self.assertIn(b'Go Programming Essentials', response.data)

    def test_course(self):
        response = self.app.get('/course/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Course Details', response.data)

    def test_golang_course(self):
        response = self.app.get('/course/4')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Go Programming Essentials', response.data)
        self.assertIn(b'Robert Chen', response.data)

    # Contact Page Tests
    def test_contact_page_loads(self):
        """Test that contact page returns 200 status"""
        response = self.app.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contact Us', response.data)
        self.assertIn(b'Name', response.data)
        self.assertIn(b'Email', response.data)
        self.assertIn(b'Address', response.data)
        self.assertIn(b'Follow Us', response.data)

    def test_contact_form_valid_submission(self):
        """Test POST with valid data processes successfully"""
        response = self.app.post('/contact', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'address': '123 Main St, Springfield, IL 62701'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you! Your message has been sent successfully', response.data)

    def test_contact_form_missing_name(self):
        """Test POST with missing name returns error"""
        response = self.app.post('/contact', data={
            'name': '',
            'email': 'john@example.com',
            'address': '123 Main St, Springfield, IL 62701'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter your name', response.data)

    def test_contact_form_missing_email(self):
        """Test POST with missing email returns error"""
        response = self.app.post('/contact', data={
            'name': 'John Doe',
            'email': '',
            'address': '123 Main St, Springfield, IL 62701'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a valid email address', response.data)

    def test_contact_form_invalid_email(self):
        """Test POST with invalid email format returns error"""
        response = self.app.post('/contact', data={
            'name': 'John Doe',
            'email': 'notanemail',
            'address': '123 Main St, Springfield, IL 62701'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a valid email address', response.data)

    def test_contact_form_missing_address(self):
        """Test POST with missing address returns error"""
        response = self.app.post('/contact', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'address': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter your address (minimum 10 characters)', response.data)

    def test_contact_form_short_address(self):
        """Test POST with too-short address returns error"""
        response = self.app.post('/contact', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'address': 'Short'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter your address (minimum 10 characters)', response.data)

    def test_contact_form_all_empty_fields(self):
        """Test POST with all empty fields returns multiple errors"""
        response = self.app.post('/contact', data={
            'name': '',
            'email': '',
            'address': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter your name', response.data)
        self.assertIn(b'Please enter a valid email address', response.data)
        self.assertIn(b'Please enter your address (minimum 10 characters)', response.data)

class StartupBannerTestCase(unittest.TestCase):
    """Tests for the greeting printed when the service starts"""

    def test_banner_names_the_app(self):
        """Test that the banner identifies the application"""
        self.assertIn('Course Explainer', startup_banner())

    def test_banner_shows_default_url(self):
        """Test that the banner advertises the default dev server URL"""
        self.assertIn('http://127.0.0.1:5000', startup_banner())

    def test_banner_reflects_host_and_port(self):
        """Test that the banner URL follows the host/port it is given"""
        banner = startup_banner(host='0.0.0.0', port=8080)
        self.assertIn('http://0.0.0.0:8080', banner)
        self.assertNotIn('127.0.0.1', banner)

if __name__ == '__main__':
    unittest.main()