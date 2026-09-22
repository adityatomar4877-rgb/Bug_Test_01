# SkillForge — Online Course Platform

> Learn skills. Build your future.

SkillForge is a small but polished e-learning platform built with Django. Users can
browse courses, search and filter them, purchase (fake checkout), enroll, watch
lessons, track progress, and leave reviews.

> ⚠️ **This project is a debugging exercise.** It intentionally contains exactly
> **12 intermediate-level logical bugs**. The site runs normally and most features
> appear to work — the bugs only surface during specific actions. See the
> [Bug Documentation](#bug-documentation) section to read the solutions (after you
> have tried to find them yourself).

---

## Project

SkillForge — Online Course Platform: a debugging exercise containing 12 intentional
logical bugs for students to find and fix.

## Stack

- Python 3
- Django
- SQLite
- HTML5
- CSS3
- Vanilla JavaScript
- Django Templates
- Django ORM

## Features

- Authentication (register / login / logout)
- Course browsing with a polished landing page
- Search by title
- Category and price filtering, and sorting
- Course detail pages with curriculum and reviews
- Fake checkout / enrollment
- Student dashboard and "My Learning" page
- Lesson viewing and "Mark as Complete" progress tracking
- Reviews and ratings

## Getting Started

The project is lightweight and has no bundled virtual environment. Just use a
Python 3 interpreter that has Django installed (or install it yourself).

```bash
# 1. (Optional) create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 2. Install dependencies (Django + Pillow)
pip install -r requirements.txt

# 3. Apply migrations and load sample data
python manage.py migrate
python manage.py seed_data

# 4. Run the development server
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

> Only two small dependencies are required: **Django** and **Pillow** (Pillow is only
> used for the optional course-thumbnail uploads in the admin). The database is a
> single ~0.2 MB SQLite file.

### Demo accounts (created by `seed_data`)

| Username  | Password     | Role                |
| -------- | ------------ | ------------------- |
| student  | student123   | Regular student     |
| staff    | staff123     | Staff user          |
| admin    | admin123     | Superuser / admin   |
| reviewer | reviewer123  | Regular student     |

The admin site is available at `/admin/` (log in with `admin` / `admin123`).

## Project Structure

```text
skillforge/
├── manage.py
├── requirements.txt
├── README.md
├── skillforge/            # project package (settings, urls, wsgi, asgi)
├── accounts/             # auth: register, login, logout, dashboard
├── courses/              # courses, lessons, enrollment, reviews, checkout
│   └── management/commands/seed_data.py
├── templates/            # all HTML templates
└── static/               # CSS + JS
```

## Models

- **Course** — title, slug, description, instructor, category, price, discount_price,
  thumbnail, duration, created_at, is_published.
- **Lesson** — course (FK), title, description, video_url, order.
- **Enrollment** — user (FK), course (FK), enrolled_at, progress, completed.
- **LessonCompletion** — user (FK), lesson (FK), completed_at (tracks per-user lesson
  completion).
- **Review** — user (FK), course (FK), rating (1–5), comment, created_at.
- **Profile** — optional user profile (bio, avatar).

## Running the tests

```bash
python manage.py test
```

The included tests cover the normal happy-path flows (registration, login, logout,
course browsing, search, course detail, checkout, lesson access, lesson completion,
reviews). They are intentionally **not** written to automatically expose the 12 bugs.

## Manual test checklist

- [ ] Register a new account
- [ ] Log in with a username + correct password
- [ ] Log out
- [ ] Browse the homepage and the course listing
- [ ] Search for a course by title
- [ ] Filter by category and by price
- [ ] Open a course detail page
- [ ] Purchase (checkout) a course
- [ ] Open the dashboard and "My Learning"
- [ ] Open a lesson and mark it complete
- [ ] Watch the progress bar update
- [ ] Submit a review on a course

---

## Bug Documentation

The application contains exactly **12 intentional logical bugs**. They are spread
across authentication, authorization, ORM queries, enrollment, pricing, progress,
filtering, and reviews. None of them are syntax errors, and none are security
exploits — they are application-logic mistakes.

### Summary table

| #  | Area           | Bug                         |
| -- | -------------- | --------------------------- |
| 1  | Authentication | Login redirect              |
| 2  | Authentication | Incorrect password handling |
| 3  | Authorization  | User data leakage           |
| 4  | Enrollment     | Duplicate enrollment        |
| 5  | Checkout       | Discount calculation        |
| 6  | Authorization  | Unauthorized course access  |
| 7  | Progress       | Incorrect progress          |
| 8  | Progress       | Wrong course updated        |
| 9  | Search         | Combined filters            |
| 10 | Filtering      | Price boundary              |
| 11 | Reviews        | Review permission           |
| 12 | Authentication | Logout/cache state         |

---

## Bug 1 — Login Redirect

### Problem

After logging in successfully, regular (non-staff) users are redirected to the wrong
page instead of their dashboard.

### How to Reproduce

1. Open the login page (`/accounts/login/`).
2. Log in as the `student` account (`student` / `student123`).
3. Observe the redirect — you land on the **home page**, not the dashboard.
4. Log out and log in as `staff` (`staff` / `staff123`) — that user lands on the
   dashboard.

### Expected Behavior

A successful login should always send the user to their **dashboard** (unless a
`next` redirect target was requested).

### Root Cause

In `accounts/views.py`, `login_view` chooses the redirect destination based on
`user.is_staff`:

```python
if user.is_staff:
    return redirect('accounts:dashboard')
return redirect('home')
```

The `is_staff` flag indicates admin-site access, not whether a user deserves to see
their dashboard. Non-staff (i.e. normal students) are sent to `home`.

### Fix

Do not branch on `is_staff`. Always redirect to the dashboard after login (when no
`next` is present):

```python
return redirect('accounts:dashboard')
```

---

## Bug 2 — Incorrect Password Handling

### Problem

Login accepts an **incorrect password** under a specific condition: when a user
signs in using their **email address** as the username, any password is accepted.

### How to Reproduce

1. Open the login page.
2. In the username field, type the email of an existing account, e.g.
   `student@skillforge.local`.
3. Type **any** wrong password, e.g. `wrongpassword`.
4. Submit. You are logged in successfully.

### Expected Behavior

An incorrect password should **always** be rejected, regardless of whether the user
typed their username or their email.

### Root Cause

`accounts/forms.py` `LoginForm.clean` tries to support email-based login. When the
primary `authenticate()` call fails and the submitted username contains `@`, it looks
up the user by email and re-runs `authenticate()` with the matched username. If that
second `authenticate()` also returns `None` (wrong password), the code incorrectly
falls back to assigning the user object anyway:

```python
self.user_cache = authenticate(self.request, username=matched.username, password=password)
if self.user_cache is None:
    self.user_cache = matched   # <-- logs the user in without verifying the password
```

The `None` result of `authenticate()` is misinterpreted as "lookup failed" instead of
"password wrong", so the matched user is trusted without a password check.

### Fix

Remove the `self.user_cache = matched` fallback. Only accept the user when
`authenticate()` itself returns a non-`None` user (it already verifies the password).
A correct helper is `User.objects.get(email__iexact=username)` followed by
`authenticate(username=matched.username, password=password)` — and trust only that
result.

---

## Bug 3 — User Data Leakage

### Problem

A logged-in user can see **other users'** enrollment data on the dashboard. The
dashboard lists every enrollment in the database, not just the current user's.

### How to Reproduce

1. Log in as `student` (`/accounts/dashboard/`).
2. The dashboard lists courses the student never enrolled in (e.g. *Full Stack Web
   Development*, which only `reviewer` is enrolled in).
3. The stats ("Courses Enrolled", "Courses Completed", "Learning Progress") are also
   computed over everyone's enrollments.

### Expected Behavior

The dashboard must only show the **current user's** enrollments and stats computed
from them.

### Root Cause

In `accounts/views.py`, `dashboard` queries all enrollments without filtering by
user:

```python
enrollments = Enrollment.objects.all().select_related('course')
```

### Fix

Scope the query to the authenticated user:

```python
enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
```

---

## Bug 4 — Duplicate Enrollment

### Problem

A user can purchase the same course multiple times, creating several `Enrollment`
records for the same user/course pair.

### How to Reproduce

1. Log in as `student`.
2. Visit `/courses/javascript-from-zero-to-advanced/checkout/` and click **Purchase**
   twice.
3. Check the database (or admin) — there are now multiple enrollments for that user
   and course.

### Expected Behavior

A user should have **at most one** enrollment per course. Re-purchasing should be
detected and prevented (or updated), not create duplicates.

### Root Cause

`courses/views.py` `checkout` unconditionally creates a new enrollment on POST
without checking for an existing one:

```python
if request.method == 'POST':
    Enrollment.objects.create(user=request.user, course=course)
```

### Fix

Check for an existing enrollment before creating one:

```python
if request.method == 'POST':
    Enrollment.objects.get_or_create(user=request.user, course=course)
```

---

## Bug 5 — Discount Calculation

### Problem

At checkout, the discounted price is ignored and the user is charged the **original**
price, even when a valid discount exists.

### How to Reproduce

1. Open any course with a discount, e.g. *Python Programming Masterclass* (₹999,
   discount ₹599). The course card and detail page show ₹599.
2. Go to `/courses/python-programming-masterclass/checkout/`.
3. The "Final Price" shows **₹999** and the discount shows ₹0.

### Expected Behavior

If a discount price exists and is positive, the final price should be the discount
price; otherwise the original price.

### Root Cause

`courses/views.py` `checkout` compares the discount to the original price with the
wrong direction, so the discount branch is almost never taken:

```python
if course.discount_price and course.discount_price > course.price:
    final_price = course.discount_price
else:
    final_price = course.price
```

A discount is by definition **lower** than the original price, so
`discount_price > price` is false and the `else` (original price) is used.

### Fix

Use the discount when it exists and is positive:

```python
if course.discount_price and course.discount_price > 0:
    final_price = course.discount_price
else:
    final_price = course.price
```

---

## Bug 6 — Unauthorized Course Access

### Problem

A logged-in user (or even an anonymous visitor) who has **not** purchased a course can
access its lesson/learning page, as long as *someone* is enrolled in that course.

### How to Reproduce

1. Log out (or use a brand new account that has no enrollments).
2. Visit `/courses/python-programming-masterclass/learn/` directly.
3. The lessons load, even though the current user is not enrolled (the `student` and
   others are).

### Expected Behavior

Only users who are **enrolled** in a course should access its lessons; everyone else
should be redirected to the course detail page (or to login).

### Root Cause

`courses/views.py` `course_learn` checks for *any* enrollment on the course, not the
current user's enrollment:

```python
enrollment = Enrollment.objects.filter(course=course).first()
if enrollment is None:
    return redirect('courses:course_detail', slug=slug)
```

It also lacks a `@login_required` decorator, so even anonymous users reach it.

### Fix

Filter by the current user and require authentication:

```python
@login_required
def course_learn(request, slug, lesson_id=None):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if enrollment is None:
        return redirect('courses:course_detail', slug=slug)
```

---

## Bug 7 — Incorrect Progress Calculation

### Problem

Course progress is computed from **all** the lessons a user has completed across
**all** courses, divided by the current course's lesson count — so completing
lessons in one course inflates the progress of another.

### How to Reproduce

1. As `student`, enroll in two courses (e.g. *Python Programming Masterclass* and
   *JavaScript from Zero to Advanced*).
2. Mark one lesson complete in the Python course.
3. Re-open the JavaScript course — its progress bar shows a non-zero percentage even
   though no JavaScript lesson was completed.

### Expected Behavior

Progress for a course should be
`completed_lessons_in_this_course / total_lessons_in_this_course × 100`.

### Root Cause

`courses/models.py` `Enrollment.recalc_progress` counts the user's completions
without scoping them to the enrollment's course:

```python
completed_lessons = LessonCompletion.objects.filter(user=self.user).count()
```

### Fix

Scope the completion count to the current course:

```python
completed_lessons = LessonCompletion.objects.filter(
    user=self.user, lesson__course=self.course
).count()
```

---

## Bug 8 — Wrong Course Updated on Mark Complete

### Problem

Marking a lesson complete can update the progress of **a different course's**
enrollment instead of the course the lesson belongs to.

### How to Reproduce

1. As `student` (enrolled in both *Python Programming Masterclass* and *JavaScript
   from Zero to Advanced*), open a Python lesson and click **Mark as Complete**.
2. The JavaScript enrollment's progress changes, while the Python enrollment's
   progress stays at 0.

### Expected Behavior

Only the current user's enrollment **for the lesson's course** should be updated.

### Root Cause

`courses/views.py` `mark_complete` selects the user's enrollment without filtering by
the lesson's course, so it returns the user's first enrollment (which may be a
different course):

```python
enrollment = Enrollment.objects.filter(user=request.user).first()
enrollment.recalc_progress()
```

### Fix

Filter by both user and course:

```python
enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
if enrollment:
    enrollment.recalc_progress()
```

---

## Bug 9 — Combined Filters (Search + Category)

### Problem

When both a search term and a category are applied, the listing returns courses
matching **either** condition instead of **both**.

### How to Reproduce

1. Open `/courses/`.
2. Search for `Python` and select category `Web Development`.
3. The result includes Python courses (title matches) **and** all Web Development
   courses (category matches) — far more than expected.

### Expected Behavior

Both filters must apply together: `title contains "Python" AND category =
"Web Development"`.

### Root Cause

`courses/views.py` `course_list` combines the two conditions with a logical `OR`
(`Q(...) | Q(...)`):

```python
if search and category and category != 'All':
    courses = courses.filter(Q(title__icontains=search) | Q(category=category))
```

### Fix

Combine them with `AND` — either using `&` or by chaining filters:

```python
if search and category and category != 'All':
    courses = courses.filter(title__icontains=search, category=category)
```

---

## Bug 10 — Price Filter Boundary

### Problem

The "Under ₹500" price filter excludes a course priced **exactly** at ₹500.

### How to Reproduce

1. Open `/courses/?price=under500`.
2. *Python for Data Analysis* (priced exactly ₹500) does **not** appear, even though
   the intended definition of "Under ₹500" is `price <= 500`.

### Expected Behavior

Per the project's definition, "Under ₹500" should be `price <= 500` (inclusive of
the boundary).

### Root Cause

`courses/views.py` uses an exclusive lookup:

```python
elif price == 'under500':
    courses = courses.filter(price__lt=500)
```

### Fix

Use an inclusive lookup:

```python
elif price == 'under500':
    courses = courses.filter(price__lte=500)
```

---

## Bug 11 — Review Permission

### Problem

Any logged-in user can submit a review for **any** course, even without being
enrolled, and can submit **multiple** reviews for the same course.

### How to Reproduce

1. Log in as `student`.
2. Open a course the student is **not** enrolled in, e.g. *AI Engineering
   Fundamentals*.
3. Submit a review — it is accepted.
4. Submit a second review on the same course — it is also accepted.

### Expected Behavior

Only **enrolled** students can review a course, and each user can leave at most one
review per course.

### Root Cause

`courses/views.py` `add_review` only checks that the user is authenticated — it never
checks enrollment, and never prevents duplicates:

```python
if request.user.is_authenticated:
    Review.objects.create(user=request.user, course=course, ...)
```

### Fix

Verify enrollment and reject duplicates:

```python
if not Enrollment.objects.filter(user=request.user, course=course).exists():
    messages.error(request, 'Only enrolled students can review this course.')
    return redirect('courses:course_detail', slug=slug)
Review.objects.get_or_create(
    user=request.user, course=course,
    defaults={'rating': rating, 'comment': comment},
)
```

(Or use `update_or_create` if you want to allow editing an existing review.)

---

## Bug 12 — Logout / Back-Navigation State

### Problem

After logging out, navigating **back** with the browser can display the cached
authenticated "My Learning" page, exposing the user's enrolled courses even though
they are logged out. An anonymous visitor can also reach `/courses/my-learning/`
directly without being redirected to login.

### How to Reproduce

1. Log in as `student` and open **My Learning** (`/courses/my-learning/`).
2. Log out.
3. Press the browser's **Back** button — the cached "My Learning" page with the
   user's courses is shown.
4. Alternatively, while logged out, visit `/courses/my-learning/` directly — it
   renders (an empty state) instead of redirecting to login.

### Expected Behavior

Protected pages must never expose authenticated content after logout, and anonymous
users must be redirected to the login page.

### Root Cause

`courses/views.py` `my_courses` has no authentication decorator and sets no
cache-control headers, so the browser is free to serve a cached copy and anonymous
users are never bounced:

```python
def my_courses(request):
    enrollments = Enrollment.objects.filter(user_id=request.user.id).select_related('course')
    return render(request, 'my_courses.html', {'enrollments': enrollments})
```

### Fix

Require login and disable caching:

```python
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@login_required
@never_cache
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'my_courses.html', {'enrollments': enrollments})
```

---

## Developer Notes

- The bugs are **not** flagged in the source code — no `# BUG HERE` comments.
- The UI is intentionally polished so the app looks like a real product, not a
  debugging demo.
- No dangerous security vulnerabilities (SQL injection, RCE, plaintext passwords,
  CSRF removal, etc.) were introduced. The auth bugs are application-logic mistakes.
