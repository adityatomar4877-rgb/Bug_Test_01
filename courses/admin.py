from django.contrib import admin
from .models import Course, Lesson, Enrollment, Review, LessonCompletion


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'discount_price', 'is_published', 'student_count')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'instructor')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]

    def student_count(self, obj):
        return obj.enrollments.count()
    student_count.short_description = 'Students'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress', 'completed', 'enrolled_at')
    list_filter = ('completed', 'course')
    search_fields = ('user__username', 'course__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course')
    search_fields = ('user__username', 'course__title')


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')
    search_fields = ('user__username', 'lesson__title')
