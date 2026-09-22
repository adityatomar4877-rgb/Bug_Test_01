from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Course, Lesson, Review, Enrollment


COURSES = [
    {
        'title': 'Python Programming Masterclass',
        'instructor': 'Dr. Aarti Sharma',
        'category': 'Python',
        'price': 999,
        'discount_price': 599,
        'duration': '18 hours',
        'description': 'Master Python from the ground up. Covers syntax, data structures, OOP, file handling, exceptions, and real-world projects to make you job-ready.',
        'lessons': [
            'Getting Started with Python',
            'Variables, Types and Operators',
            'Control Flow and Loops',
            'Functions and Modules',
            'Object-Oriented Programming',
            'Working with Files and Exceptions',
        ],
    },
    {
        'title': 'Full Stack Web Development',
        'instructor': 'Rahul Verma',
        'category': 'Web Development',
        'price': 1499,
        'discount_price': 999,
        'duration': '32 hours',
        'description': 'Build modern web applications end-to-end. Learn HTML, CSS, JavaScript, Django, databases, and deployment in one complete journey.',
        'lessons': [
            'Web Fundamentals',
            'HTML and CSS Deep Dive',
            'Responsive Design',
            'JavaScript Essentials',
            'Django Backend Development',
            'Databases and ORM',
            'Deployment and DevOps',
        ],
    },
    {
        'title': 'JavaScript from Zero to Advanced',
        'instructor': 'Meera Nair',
        'category': 'JavaScript',
        'price': 799,
        'discount_price': 499,
        'duration': '22 hours',
        'description': 'Go from beginner to advanced in JavaScript. ES6+, async programming, the DOM, APIs, and modern patterns used in real projects.',
        'lessons': [
            'JavaScript Basics',
            'Functions and Scope',
            'Objects and Arrays',
            'Asynchronous JavaScript',
            'The DOM and Events',
            'Modern ES6+ Features',
        ],
    },
    {
        'title': 'Cyber Security Fundamentals',
        'instructor': 'Kabir Singh',
        'category': 'Cyber Security',
        'price': 1200,
        'discount_price': 800,
        'duration': '16 hours',
        'description': 'Understand how attackers think and how to defend systems. Covers threats, cryptography basics, network security, and secure practices.',
        'lessons': [
            'Introduction to Cyber Security',
            'Common Threats and Attacks',
            'Cryptography Basics',
            'Network Security',
            'Securing Applications',
        ],
    },
    {
        'title': 'Ethical Hacking Essentials',
        'instructor': 'Kabir Singh',
        'category': 'Cyber Security',
        'price': 1999,
        'discount_price': 1499,
        'duration': '26 hours',
        'description': 'Learn ethical hacking hands-on. Reconnaissance, scanning, exploitation basics, and how to report vulnerabilities responsibly.',
        'lessons': [
            'Ethics and Legal Basics',
            'Reconnaissance',
            'Scanning and Enumeration',
            'Exploitation Basics',
            'Web Application Testing',
            'Reporting and Mitigation',
        ],
    },
    {
        'title': 'Machine Learning Fundamentals',
        'instructor': 'Dr. Lena Fischer',
        'category': 'AI',
        'price': 1799,
        'discount_price': 1299,
        'duration': '24 hours',
        'description': 'A practical introduction to machine learning. Regression, classification, clustering, and model evaluation with real datasets.',
        'lessons': [
            'ML Landscape',
            'Supervised Learning',
            'Unsupervised Learning',
            'Model Evaluation',
            'Feature Engineering',
            'Mini Project',
        ],
    },
    {
        'title': 'UI/UX Design Bootcamp',
        'instructor': 'Sara Kapoor',
        'category': 'UI/UX',
        'price': 999,
        'discount_price': None,
        'duration': '20 hours',
        'description': 'Design beautiful, usable products. Learn user research, wireframing, prototyping, and design systems from a working designer.',
        'lessons': [
            'Design Thinking',
            'User Research',
            'Wireframing',
            'Prototyping',
            'Design Systems',
        ],
    },
    {
        'title': 'React Development',
        'instructor': 'Rahul Verma',
        'category': 'Web Development',
        'price': 899,
        'discount_price': 599,
        'duration': '19 hours',
        'description': 'Build fast, modern UIs with React. Components, hooks, state management, and integration with APIs in real projects.',
        'lessons': [
            'React Basics',
            'Components and Props',
            'State and Hooks',
            'Routing',
            'Fetching Data',
        ],
    },
    {
        'title': 'Data Science with Python',
        'instructor': 'Dr. Aarti Sharma',
        'category': 'Data Science',
        'price': 1599,
        'discount_price': 999,
        'duration': '28 hours',
        'description': 'The complete data science path with Python. Pandas, NumPy, visualization, and an end-to-end analysis project.',
        'lessons': [
            'Data Science Workflow',
            'NumPy Essentials',
            'Pandas in Depth',
            'Data Visualization',
            'Exploratory Analysis',
            'Capstone Project',
        ],
    },
    {
        'title': 'AI Engineering Fundamentals',
        'instructor': 'Dr. Lena Fischer',
        'category': 'AI',
        'price': 2499,
        'discount_price': 1799,
        'duration': '34 hours',
        'description': 'Step into AI engineering. Build and deploy intelligent systems, from neural networks to production APIs.',
        'lessons': [
            'AI Engineering Overview',
            'Neural Networks',
            'Training and Tuning',
            'Deployment Patterns',
            'LLMs and APIs',
            'MLOps Basics',
            'Final Project',
        ],
    },
    {
        'title': 'Python for Data Analysis',
        'instructor': 'Meera Nair',
        'category': 'Python',
        'price': 500,
        'discount_price': 299,
        'duration': '12 hours',
        'description': 'Use Python to analyze data confidently. Clean data, compute statistics, and create clear visualizations.',
        'lessons': [
            'Setting Up Your Environment',
            'Reading and Cleaning Data',
            'Summarizing Data',
            'Visualizing Insights',
        ],
    },
    {
        'title': 'JavaScript DOM Projects',
        'instructor': 'Meera Nair',
        'category': 'JavaScript',
        'price': 0,
        'discount_price': None,
        'duration': '8 hours',
        'description': 'A free, project-based intro to the DOM. Build interactive UI features with vanilla JavaScript.',
        'lessons': [
            'Selecting Elements',
            'Events and Interactivity',
            'A Mini Project',
        ],
    },
]


def slugify(title):
    return title.lower().replace(':', '').replace(',', '').replace('.', '').replace('/', '-').replace('  ', ' ').strip().replace(' ', '-')


class Command(BaseCommand):
    help = 'Seed the database with sample courses, lessons, demo users and reviews.'

    def handle(self, *args, **options):
        student, _ = User.objects.get_or_create(
            username='student',
            defaults={'email': 'student@skillforge.local', 'is_staff': False, 'is_active': True},
        )
        student.set_password('student123')
        student.save()

        staff, _ = User.objects.get_or_create(
            username='staff',
            defaults={'email': 'staff@skillforge.local', 'is_staff': True, 'is_active': True},
        )
        staff.set_password('staff123')
        staff.save()

        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@skillforge.local', 'is_staff': True, 'is_superuser': True, 'is_active': True},
        )
        admin.set_password('admin123')
        admin.save()

        reviewer, _ = User.objects.get_or_create(
            username='reviewer',
            defaults={'email': 'reviewer@skillforge.local', 'is_staff': False, 'is_active': True},
        )
        reviewer.set_password('reviewer123')
        reviewer.save()

        for data in COURSES:
            slug = slugify(data['title'])
            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': data['title'],
                    'instructor': data['instructor'],
                    'category': data['category'],
                    'price': data['price'],
                    'discount_price': data['discount_price'],
                    'duration': data['duration'],
                    'description': data['description'],
                    'is_published': True,
                },
            )
            if created:
                for idx, lesson_title in enumerate(data['lessons'], start=1):
                    Lesson.objects.create(
                        course=course,
                        title=lesson_title,
                        description=f'{lesson_title} — a hands-on lesson in {course.title}.',
                        order=idx,
                    )

        py_master = Course.objects.get(slug=slugify('Python Programming Masterclass'))
        js_course = Course.objects.get(slug=slugify('JavaScript from Zero to Advanced'))
        web_course = Course.objects.get(slug=slugify('Full Stack Web Development'))

        Enrollment.objects.get_or_create(user=student, course=py_master)
        Enrollment.objects.get_or_create(user=student, course=js_course)
        Enrollment.objects.get_or_create(user=reviewer, course=web_course)

        Review.objects.get_or_create(
            user=student, course=py_master,
            defaults={'rating': 5, 'comment': 'Excellent course! The projects really helped me learn Python.'},
        )
        Review.objects.get_or_create(
            user=reviewer, course=web_course,
            defaults={'rating': 4, 'comment': 'Great coverage of full stack concepts. A bit fast in places.'},
        )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully.'))
        self.stdout.write('Demo users:')
        self.stdout.write('  student  / student123  (regular student)')
        self.stdout.write('  staff    / staff123    (staff user)')
        self.stdout.write('  admin    / admin123    (superuser)')
        self.stdout.write('  reviewer / reviewer123 (regular student)')
