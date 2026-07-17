from django.urls import path
from . import views

app_name = 'teacher_dashboard'

urlpatterns = [
    # Subject Management
    path('subjects/', views.manage_subjects, name='manage_subjects'),
    
    # Exam Management
    path('create-exam/', views.create_exam, name='create_exam'),
    path('my-exams/', views.my_exams, name='my_exams'),
    path('exam/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('exam/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('exam/<int:exam_id>/results/', views.exam_results, name='exam_results'),
    path('exam/<int:exam_id>/toggle-status/', views.toggle_exam_status, name='toggle_exam_status'),
    
    # All Results
    path('all-results/', views.all_results, name='all_results'),
    
    # Student Result Actions
    path('student-result/<int:attempt_id>/', views.view_student_result, name='view_student_result'),
    path('delete-attempt/<int:attempt_id>/', views.delete_student_attempt, name='delete_student_attempt'),
]