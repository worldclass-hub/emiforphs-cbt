from django.urls import path
from . import views

app_name = 'student_portal'

urlpatterns = [
    # ============================================================
    # BECE EXAM ROUTES
    # ============================================================
    path('bece-dashboard/', views.bece_dashboard, name='bece_dashboard'),
    path('start-bece-exam/', views.start_bece_exam, name='start_bece_exam'),
    path('take-bece-exam/', views.take_bece_exam, name='take_bece_exam'),
    path('take-bece-exam-session/<int:attempt_id>/', views.take_bece_exam_session, name='take_bece_exam_session'),
    path('submit-bece-answer/<int:attempt_id>/', views.submit_bece_answer, name='submit_bece_answer'),
    path('save-bece-answer/<int:attempt_id>/', views.save_bece_answer, name='save_bece_answer'),
    path('get-bece-progress/<int:attempt_id>/', views.get_bece_progress, name='get_bece_progress'),
    path('finish-bece-exam/<int:attempt_id>/', views.finish_bece_exam, name='finish_bece_exam'),
    path('quit-bece-exam/<int:attempt_id>/', views.quit_bece_exam, name='quit_bece_exam'),
    
    # ============================================================
    # SCHOOL EXAMS (NORMAL) - Using StudentAttempt
    # ============================================================
    path('school-exams/', views.school_exams_dashboard, name='school_exams_dashboard'),
    path('start-school-exam/<int:exam_id>/', views.start_school_exam, name='start_school_exam'),
    
    # StudentAttempt routes (School Exams)
    path('take-exam/<int:attempt_id>/', views.take_exam, name='take_exam'),
    path('save-answer/<int:attempt_id>/', views.save_answer, name='save_answer'),
    path('get-progress/<int:attempt_id>/', views.get_progress, name='get_progress'),
    path('submit-exam/<int:attempt_id>/', views.submit_exam, name='submit_exam'),
    path('finish-exam/<int:attempt_id>/', views.finish_exam, name='finish_exam'),
    path('quit-exam/<int:attempt_id>/', views.quit_exam, name='quit_exam'),
    
    # ============================================================
    # RESULTS
    # ============================================================
    path('result/<int:attempt_id>/', views.view_result, name='view_result'),
    
    # ============================================================
    # ORIGINAL STUDENT PORTAL VIEWS
    # ============================================================
    path('available-exams/', views.available_exams, name='available_exams'),
    path('my-results/', views.my_results, name='my_results'),
]