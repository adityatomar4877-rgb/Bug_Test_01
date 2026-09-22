from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('my-learning/', views.my_courses, name='my_courses'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/checkout/', views.checkout, name='checkout'),
    path('<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('<slug:slug>/learn/<int:lesson_id>/', views.course_learn, name='course_learn_lesson'),
    path('lesson/<int:lesson_id>/complete/', views.mark_complete, name='mark_complete'),
    path('<slug:slug>/review/', views.add_review, name='add_review'),
]
