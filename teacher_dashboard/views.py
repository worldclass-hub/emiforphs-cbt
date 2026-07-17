from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from exams.models import Exam, Subject, Question, ExamCategory, StudentAttempt
from django.db.models import Count

@login_required
def manage_subjects(request):
    """Manage school subjects (add, view, delete)"""
    # Only teachers and admins can manage subjects
    if request.user.role not in ['TEACHER', 'ADMIN']:
        messages.error(request, 'You are not authorized to manage subjects.')
        return redirect('dashboard')
    
    subjects = Subject.objects.filter(category='NORMAL').order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            subject_name = request.POST.get('subject_name', '').strip()
            if subject_name:
                # Check if subject already exists
                if Subject.objects.filter(name__iexact=subject_name, category='NORMAL').exists():
                    messages.error(request, f'Subject "{subject_name}" already exists.')
                else:
                    Subject.objects.create(name=subject_name, category='NORMAL')
                    messages.success(request, f'✅ Subject "{subject_name}" created successfully!')
            else:
                messages.error(request, 'Please enter a subject name.')
        
        elif action == 'delete':
            subject_id = request.POST.get('subject_id')
            try:
                subject = Subject.objects.get(id=subject_id, category='NORMAL')
                subject_name = subject.name
                # Check if subject is being used in any exam
                if Exam.objects.filter(subject=subject).exists():
                    messages.error(request, f'Cannot delete "{subject_name}" because it is being used in exams.')
                else:
                    subject.delete()
                    messages.success(request, f'✅ Subject "{subject_name}" deleted successfully.')
            except Subject.DoesNotExist:
                messages.error(request, 'Subject not found.')
        
        return redirect('teacher_dashboard:manage_subjects')
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'teacher_dashboard/manage_subjects.html', context)

@login_required
def create_exam(request):
    """Create a new exam (NORMAL category only)"""
    # Only teachers and admins can create exams
    if request.user.role not in ['TEACHER', 'ADMIN']:
        messages.error(request, 'You are not authorized to create exams.')
        return redirect('dashboard')
    
    # Get all NORMAL subjects for the dropdown
    subjects = Subject.objects.filter(category='NORMAL').order_by('name')
    
    # If no subjects exist, show a message
    if not subjects.exists():
        messages.warning(request, 'No subjects available. Please add a subject first.')
        return render(request, 'teacher_dashboard/create_exam.html', {
            'subjects': subjects,
            'class_levels': ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3'],
            'terms': ['First Term', 'Second Term', 'Third Term'],
            'no_subjects': True,
        })
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        duration = request.POST.get('duration', 45)
        instructions = request.POST.get('instructions', '')
        class_level = request.POST.get('class_level')
        term = request.POST.get('term')
        session = request.POST.get('session', '2024/2025')
        
        # Validate
        if not title or not subject_id:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'teacher_dashboard/create_exam.html', {
                'subjects': subjects,
                'class_levels': ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3'],
                'terms': ['First Term', 'Second Term', 'Third Term'],
            })
        
        # Create exam
        exam = Exam.objects.create(
            title=title,
            category=ExamCategory.NORMAL,
            subject_id=subject_id,
            duration_minutes=int(duration),
            instructions=instructions,
            class_level=class_level,
            term=term,
            session=session,
            created_by=request.user,
            is_active=True
        )
        
        messages.success(request, f'✅ Exam "{title}" created successfully! Now add questions.')
        return redirect('teacher_dashboard:edit_exam', exam_id=exam.id)
    
    # GET request - show form
    context = {
        'subjects': subjects,
        'class_levels': ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3'],
        'terms': ['First Term', 'Second Term', 'Third Term'],
        'no_subjects': False,
    }
    return render(request, 'teacher_dashboard/create_exam.html', context)

@login_required
def my_exams(request):
    """View all exams created by the teacher"""
    exams = Exam.objects.filter(
        created_by=request.user,
        category='NORMAL'
    ).annotate(
        attempts_count=Count('attempts')
    ).order_by('-created_at')
    
    context = {
        'exams': exams,
    }
    return render(request, 'teacher_dashboard/my_exams.html', context)

@login_required
def edit_exam(request, exam_id):
    """Edit exam and manage questions"""
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all().order_by('question_number')
    
    if request.method == 'POST':
        # Check if deleting a question
        delete_question_id = request.POST.get('delete_question_id')
        if delete_question_id:
            try:
                q = Question.objects.get(id=delete_question_id, exam=exam)
                q.delete()
                exam.update_total_questions()
                messages.success(request, 'Question deleted successfully.')
            except Question.DoesNotExist:
                messages.error(request, 'Question not found.')
            return redirect('teacher_dashboard:edit_exam', exam_id=exam.id)
        
        # Add new question
        question_text = request.POST.get('question_text')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c')
        option_d = request.POST.get('option_d')
        correct_answer = request.POST.get('correct_answer')
        
        if all([question_text, option_a, option_b, option_c, option_d, correct_answer]):
            next_number = questions.count() + 1
            Question.objects.create(
                exam=exam,
                question_number=next_number,
                text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                marks=1
            )
            exam.update_total_questions()
            messages.success(request, '✅ Question added successfully!')
        else:
            messages.error(request, 'Please fill in all fields for the question.')
        
        return redirect('teacher_dashboard:edit_exam', exam_id=exam.id)
    
    context = {
        'exam': exam,
        'questions': questions,
    }
    return render(request, 'teacher_dashboard/edit_exam.html', context)

@login_required
def delete_exam(request, exam_id):
    """Delete an exam"""
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    
    if request.method == 'POST':
        exam_title = exam.title
        exam.delete()
        messages.success(request, f'✅ Exam "{exam_title}" deleted successfully.')
        return redirect('teacher_dashboard:my_exams')
    
    return redirect('teacher_dashboard:my_exams')

@login_required
def exam_results(request, exam_id):
    """View results for a specific exam"""
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    attempts = exam.attempts.filter(status='COMPLETED').order_by('-submitted_at')
    
    context = {
        'exam': exam,
        'attempts': attempts,
    }
    return render(request, 'teacher_dashboard/exam_results.html', context)

@login_required
def toggle_exam_status(request, exam_id):
    """Activate or deactivate an exam"""
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    
    if request.method == 'POST':
        exam.is_active = not exam.is_active
        exam.save()
        status = "activated" if exam.is_active else "deactivated"
        messages.success(request, f'✅ Exam "{exam.title}" {status} successfully.')
    
    return redirect('teacher_dashboard:my_exams')

@login_required
def all_results(request):
    """View all student results across all exams created by the teacher"""
    # Only teachers and admins can view results
    if request.user.role not in ['TEACHER', 'ADMIN']:
        messages.error(request, 'You are not authorized to view results.')
        return redirect('dashboard')
    
    # Get all exams created by this teacher
    exams = Exam.objects.filter(
        created_by=request.user,
        category='NORMAL',
        is_active=True
    )
    
    # Get all attempts for these exams
    attempts = StudentAttempt.objects.filter(
        exam__in=exams,
        status='COMPLETED'
    ).select_related('student', 'exam', 'exam__subject').order_by('-submitted_at')
    
    # Calculate statistics
    total_students = attempts.values('student').distinct().count()
    total_exams = exams.count()
    
    context = {
        'attempts': attempts,
        'total_students': total_students,
        'total_exams': total_exams,
    }
    return render(request, 'teacher_dashboard/all_results.html', context)

@login_required
def view_student_result(request, attempt_id):
    """View a specific student's result in detail"""
    # Only teachers and admins can view results
    if request.user.role not in ['TEACHER', 'ADMIN']:
        messages.error(request, 'You are not authorized to view results.')
        return redirect('dashboard')
    
    attempt = get_object_or_404(StudentAttempt, id=attempt_id)
    
    # Check if the teacher owns this exam
    if attempt.exam.created_by != request.user and request.user.role != 'ADMIN':
        messages.error(request, 'You are not authorized to view this result.')
        return redirect('teacher_dashboard:all_results')
    
    # Get questions with answers
    questions = attempt.exam.questions.all().order_by('question_number')
    
    # Build question data with user answers
    question_data = []
    correct_count = 0
    for question in questions:
        user_answer = attempt.answers.get(str(question.id))
        is_correct = user_answer == question.correct_answer
        if is_correct:
            correct_count += 1
        question_data.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
        })
    
    context = {
        'attempt': attempt,
        'exam': attempt.exam,
        'student': attempt.student,
        'score': attempt.score,
        'total': attempt.total_questions,
        'percentage': attempt.percentage(),
        'question_data': question_data,
        'correct_count': correct_count,
        'wrong_count': attempt.total_questions - correct_count,
    }
    return render(request, 'teacher_dashboard/view_student_result.html', context)

@login_required
def delete_student_attempt(request, attempt_id):
    """Delete a student's exam attempt"""
    # Only teachers and admins can delete attempts
    if request.user.role not in ['TEACHER', 'ADMIN']:
        messages.error(request, 'You are not authorized to delete attempts.')
        return redirect('dashboard')
    
    attempt = get_object_or_404(StudentAttempt, id=attempt_id)
    
    # Check if the teacher owns this exam
    if attempt.exam.created_by != request.user and request.user.role != 'ADMIN':
        messages.error(request, 'You are not authorized to delete this attempt.')
        return redirect('teacher_dashboard:all_results')
    
    if request.method == 'POST':
        student_name = attempt.student.username
        exam_title = attempt.exam.title
        attempt.delete()
        messages.success(request, f'✅ Deleted {student_name}\'s attempt for "{exam_title}".')
        return redirect('teacher_dashboard:all_results')
    
    return redirect('teacher_dashboard:all_results')