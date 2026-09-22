from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    instructor = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, null=True, blank=True
    )
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    duration = models.CharField(max_length=50, default='10 hours')
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})

    @property
    def effective_price(self):
        if self.discount_price and self.discount_price > 0:
            return self.discount_price
        return self.price

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    @property
    def rating_count(self):
        return self.reviews.count()

    @property
    def student_count(self):
        return self.enrollments.count()

    @property
    def is_free(self):
        return self.effective_price == 0


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True, default='https://example.com/placeholder.mp4')
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'

    def recalc_progress(self):
        total_lessons = self.course.lessons.count()
        if not total_lessons:
            self.progress = 0
            self.completed = False
            self.save()
            return self.progress
        completed_lessons = LessonCompletion.objects.filter(user=self.user).count()
        self.progress = int((completed_lessons / total_lessons) * 100)
        if self.progress > 100:
            self.progress = 100
        self.completed = self.progress >= 100
        self.save()
        return self.progress


class LessonCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_completions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f'{self.user.username} - {self.lesson.title}'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.course.title} - {self.rating} stars'
