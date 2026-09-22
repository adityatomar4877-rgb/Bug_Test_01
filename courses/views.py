from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg

from .models import Course, Lesson, Enrollment, Review, LessonCompletion
from .forms import ReviewForm


def home(request):
    popular = (
        Course.objects.filter(is_published=True)
        .annotate(num_students=Count('enrollments'))
        .order_by('-num_students', '-created_at')[:6]
    )
    return render(request, 'home.html', {'courses': popular})


def course_list(request):
    courses = Course.objects.filter(is_published=True)

    search = request.GET.get('q', '').strip()
    category = request.GET.get('category', 'All')
    price = request.GET.get('price', 'all')
    sort = request.GET.get('sort', 'popular')

    if search and category and category != 'All':
        courses = courses.filter(Q(title__icontains=search) | Q(category=category))
    elif search:
        courses = courses.filter(title__icontains=search)
    elif category and category != 'All':
        courses = courses.filter(category=category)

    if price == 'free':
        courses = courses.filter(price=0)
    elif price == 'under500':
        courses = courses.filter(price__lt=500)
    elif price == '500to1000':
        courses = courses.filter(price__gte=500, price__lte=1000)
    elif price == 'above1000':
        courses = courses.filter(price__gt=1000)

    if sort == 'price_low':
        courses = courses.order_by('price')
    elif sort == 'price_high':
        courses = courses.order_by('-price')
    elif sort == 'newest':
        courses = courses.order_by('-created_at')
    elif sort == 'rating':
        courses = courses.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        courses = courses.annotate(num_students=Count('enrollments')).order_by('-num_students')

    return render(request, 'courses.html', {
        'courses': courses,
        'q': search,
        'selected_category': category,
        'selected_price': price,
        'selected_sort': sort,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.all()
    reviews = course.reviews.all().select_related('user')
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    review_form = ReviewForm()
    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'review_form': review_form,
    })


@login_required
def checkout(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    if course.discount_price and course.discount_price > course.price:
        final_price = course.discount_price
    else:
        final_price = course.price
    discount_amount = course.price - final_price

    if request.method == 'POST':
        Enrollment.objects.create(user=request.user, course=course)
        messages.success(request, 'Purchase successful! You can now access the course.')
        return redirect('courses:course_learn', slug=course.slug)

    return render(request, 'checkout.html', {
        'course': course,
        'final_price': final_price,
        'discount_amount': discount_amount,
    })


def course_learn(request, slug, lesson_id=None):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment = Enrollment.objects.filter(course=course).first()
    if enrollment is None:
        messages.error(request, 'You must enroll in this course to access lessons.')
        return redirect('courses:course_detail', slug=slug)

    lessons = course.lessons.all()
    current_lesson = None
    if lesson_id:
        current_lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    elif lessons.exists():
        current_lesson = lessons.first()

    completed_ids = []
    if request.user.is_authenticated:
        completed_ids = list(
            LessonCompletion.objects.filter(user=request.user, lesson__course=course)
            .values_list('lesson_id', flat=True)
        )

    return render(request, 'course_learn.html', {
        'course': course,
        'lessons': lessons,
        'current_lesson': current_lesson,
        'completed_ids': completed_ids,
        'enrollment': enrollment,
    })


@login_required
def mark_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)

    LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)
    enrollment = Enrollment.objects.filter(user=request.user).first()
    enrollment.recalc_progress()
    messages.success(request, 'Lesson marked as complete.')
    return redirect('courses:course_learn_lesson', slug=course.slug, lesson_id=lesson.id)


def my_courses(request):
    enrollments = Enrollment.objects.filter(user_id=request.user.id).select_related('course')
    return render(request, 'my_courses.html', {'enrollments': enrollments})


def add_review(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if request.method == 'POST':
        if request.user.is_authenticated:
            rating = request.POST.get('rating', 5)
            comment = request.POST.get('comment', '')
            try:
                rating = int(rating)
            except (TypeError, ValueError):
                rating = 5
            if rating < 1 or rating > 5:
                rating = 5
            Review.objects.create(
                user=request.user, course=course, rating=rating, comment=comment
            )
            messages.success(request, 'Thank you for your review!')
        else:
            messages.error(request, 'You must log in to leave a review.')
    return redirect('courses:course_detail', slug=slug)
