from django.test import TestCase, Client
from django.contrib.auth.models import User
from courses.models import Course, Lesson, Enrollment, Review


def make_course(slug='test-course', title='Test Course', price=800, discount=400, lessons=3):
    course = Course.objects.create(
        title=title, slug=slug, description='A test course.', instructor='Tester',
        category='Python', price=price, discount_price=discount,
        duration='5 hours', is_published=True,
    )
    for i in range(1, lessons + 1):
        Lesson.objects.create(course=course, title=f'Lesson {i}', description='desc', order=i)
    return course


class HomeAndListingTests(TestCase):
    def setUp(self):
        make_course(slug='a', title='Alpha Course', price=0, discount=None, lessons=2)
        make_course(slug='b', title='Beta Course', price=600, discount=300, lessons=2)

    def test_home_page_loads(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'SkillForge')

    def test_course_list_loads(self):
        r = self.client.get('/courses/')
        self.assertEqual(r.status_code, 200)

    def test_search_returns_matches(self):
        r = self.client.get('/courses/', {'q': 'Alpha'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Alpha Course')
        self.assertNotContains(r, 'Beta Course')

    def test_category_filter(self):
        r = self.client.get('/courses/', {'category': 'Python'})
        self.assertEqual(r.status_code, 200)

    def test_course_detail_loads(self):
        r = self.client.get('/courses/a/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Alpha Course')


class AuthTests(TestCase):
    def test_registration_creates_user_and_logs_in(self):
        r = self.client.post('/accounts/register/', {
            'username': 'newbie', 'email': 'newbie@example.com',
            'password1': 'ComplexPass123!', 'password2': 'ComplexPass123!',
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username='newbie').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_with_username_and_correct_password(self):
        User.objects.create_user(username='alice', email='alice@example.com', password='Secret123!')
        r = self.client.post('/accounts/login/', {'username': 'alice', 'password': 'Secret123!'})
        self.assertEqual(r.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_with_wrong_password_rejected(self):
        User.objects.create_user(username='bob', email='bob@example.com', password='Secret123!')
        r = self.client.post('/accounts/login/', {'username': 'bob', 'password': 'wrongpassword'})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_clears_session(self):
        User.objects.create_user(username='cara', email='cara@example.com', password='Secret123!')
        self.client.login(username='cara', password='Secret123!')
        r = self.client.post('/accounts/logout/')
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class EnrollmentAndLearningTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dan', email='dan@example.com', password='Secret123!')
        self.course = make_course(slug='py', title='Python Course', price=999, discount=599, lessons=4)
        self.client.login(username='dan', password='Secret123!')

    def test_checkout_creates_enrollment(self):
        r = self.client.post('/courses/py/checkout/')
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_enrolled_user_can_access_lessons(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        r = self.client.get('/courses/py/learn/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Python Course')

    def test_lesson_completion_updates_progress(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        lesson = self.course.lessons.first()
        r = self.client.post(f'/courses/lesson/{lesson.id}/complete/')
        self.assertEqual(r.status_code, 302)
        enrollment = Enrollment.objects.get(user=self.user, course=self.course)
        self.assertGreater(enrollment.progress, 0)

    def test_enrolled_user_can_review(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        r = self.client.post('/courses/py/review/', {'rating': '4', 'comment': 'great'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Review.objects.filter(user=self.user, course=self.course).count(), 1)
