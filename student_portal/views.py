from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count
from exams.models import Exam, Question, StudentAttempt, Subject, ExamCategory
import json
import random

# ============================================================
# ORIGINAL VIEWS (Available Exams, Results, etc.)
# ============================================================

@login_required
def available_exams(request):
    """Show all available exams for students"""
    # Get all active exams
    exams = Exam.objects.filter(is_active=True)
    
    # Filter out exams the student has already completed
    completed_exam_ids = StudentAttempt.objects.filter(
        student=request.user,
        status='COMPLETED'
    ).values_list('exam_id', flat=True)
    
    available = exams.exclude(id__in=completed_exam_ids)
    
    # Separate by category - NORMAL vs BECE
    normal_exams = available.filter(category__iexact='NORMAL')
    bece_exams = available.filter(category='BECE')
    
    context = {
        'normal_exams': normal_exams,
        'bece_exams': bece_exams,
        'completed_count': StudentAttempt.objects.filter(
            student=request.user,
            status='COMPLETED'
        ).count(),
    }
    return render(request, 'student_portal/available_exams.html', context)

@login_required
def my_results(request):
    """View all results"""
    attempts = StudentAttempt.objects.filter(
        student=request.user,
        status='COMPLETED'
    ).order_by('-submitted_at')
    
    context = {
        'attempts': attempts,
    }
    return render(request, 'student_portal/my_results.html', context)

@login_required
def view_result(request, attempt_id):
    """View a specific result from StudentAttempt"""
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    
    if attempt.status != 'COMPLETED':
        messages.warning(request, 'This exam is not yet completed.')
        return redirect('student_portal:my_results')
    
    # Get all questions for this exam
    questions = attempt.exam.questions.all().order_by('question_number')
    
    # Build subject breakdown
    subject_stats = {}
    total_correct = 0
    total_questions = 0
    
    for question in questions:
        subject = question.exam.subject.name
        
        if subject not in subject_stats:
            subject_stats[subject] = {
                'correct': 0,
                'total': 0,
                'wrong': 0,
                'questions': []
            }
        
        user_answer = attempt.answers.get(str(question.id))
        is_correct = user_answer == question.correct_answer
        
        subject_stats[subject]['total'] += 1
        if is_correct:
            subject_stats[subject]['correct'] += 1
            total_correct += 1
        else:
            subject_stats[subject]['wrong'] += 1
        
        subject_stats[subject]['questions'].append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })
        
        total_questions += 1
    
    overall_percentage = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0
    
    for subject, stats in subject_stats.items():
        stats['percentage'] = round((stats['correct'] / stats['total']) * 100, 2) if stats['total'] > 0 else 0
    
    correct_count = sum(1 for q in questions if attempt.answers.get(str(q.id)) == q.correct_answer)
    wrong_count = total_questions - correct_count
    
    context = {
        'attempt': attempt,
        'exam': attempt.exam,
        'score': attempt.score,
        'total': attempt.total_questions,
        'percentage': overall_percentage,
        'answers': attempt.answers,
        'questions': questions,
        'subject_stats': subject_stats,
        'total_correct': total_correct,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
    }
    return render(request, 'student_portal/view_result.html', context)

# ============================================================
# BECE EXAM VIEWS
# ============================================================

@login_required
def bece_dashboard(request):
    """Show BECE exam dashboard with subjects"""
    # Get all BECE subjects
    bece_subjects = Subject.objects.filter(category='BECE').order_by('name')
    
    # Check if there are any BECE exams
    has_exams = Exam.objects.filter(category='BECE', is_active=True).exists()
    
    # Count available subjects with questions
    subject_count = bece_subjects.count()
    
    # Get available years
    available_years = []
    for subject in bece_subjects:
        exam = Exam.objects.filter(category='BECE', subject=subject, is_active=True).first()
        if exam:
            years = exam.questions.filter(year__isnull=False).values_list('year', flat=True).distinct()
            available_years.extend(years)
    available_years = sorted(set(available_years), reverse=True)
    
    context = {
        'subjects': bece_subjects,
        'has_exams': has_exams,
        'subject_count': subject_count,
        'available_years': available_years,
    }
    return render(request, 'student_portal/bece_dashboard.html', context)

@login_required
def start_bece_exam(request):
    """Start a BECE exam with selected subjects"""
    if request.method != 'POST':
        return redirect('student_portal:bece_dashboard')
    
    selected_subject_ids = request.POST.getlist('subjects')
    selected_years = request.POST.getlist('years')
    
    if not selected_subject_ids:
        messages.error(request, 'Please select at least one subject.')
        return redirect('student_portal:bece_dashboard')
    
    # Store in session
    request.session['bece_subjects'] = selected_subject_ids
    request.session['bece_years'] = selected_years
    
    # ✅ FIXED: Redirect to take_bece_exam (which creates the attempt)
    return redirect('student_portal:take_bece_exam')

@login_required
def take_bece_exam(request):
    """Take a BECE exam - creates attempt and redirects to session"""
    # Get subjects from session
    subject_ids = request.session.get('bece_subjects', [])
    years = request.session.get('bece_years', [])
    
    if not subject_ids:
        messages.error(request, 'Please select subjects first.')
        return redirect('student_portal:bece_dashboard')
    
    # Get subjects
    subjects = Subject.objects.filter(id__in=subject_ids, category='BECE')
    
    # Collect questions from all selected subjects
    all_questions = []
    question_subject_map = {}
    position = 0
    
    for subject in subjects:
        exam = Exam.objects.filter(category='BECE', subject=subject, is_active=True).first()
        if exam:
            questions = exam.questions.all()
            if years:
                questions = questions.filter(year__in=years)
            questions = list(questions.order_by('?'))
            
            for q in questions:
                all_questions.append(q)
                question_subject_map[str(position)] = subject.name
                position += 1
    
    if not all_questions:
        messages.error(request, 'No questions found for your selected subjects and years.')
        return redirect('student_portal:bece_dashboard')
    
    # Use StudentAttempt for BECE
    temp_exam = Exam.objects.filter(category='BECE', is_active=True).first()
    if not temp_exam:
        messages.error(request, 'No BECE exam found.')
        return redirect('student_portal:bece_dashboard')
    
    attempt = StudentAttempt.objects.create(
        student=request.user,
        exam=temp_exam,
        total_questions=len(all_questions),
        answers={},
        status='IN_PROGRESS'
    )
    
    # Store question IDs in session
    request.session['bece_attempt_id'] = attempt.id
    request.session['bece_question_ids'] = [q.id for q in all_questions]
    request.session['bece_question_subject'] = question_subject_map
    request.session['bece_total_questions'] = len(all_questions)
    
    return redirect('student_portal:take_bece_exam_session', attempt_id=attempt.id)

@login_required
def take_bece_exam_session(request, attempt_id):
    """Take BECE exam one question at a time"""
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    
    question_ids = request.session.get('bece_question_ids', [])
    question_subject_map = request.session.get('bece_question_subject', {})
    total_questions = len(question_ids)
    
    current_position = int(request.GET.get('q', 0))
    
    if current_position >= total_questions:
        return redirect('student_portal:finish_bece_exam', attempt_id=attempt.id)
    
    question = get_object_or_404(Question, id=question_ids[current_position])
    current_subject = question_subject_map.get(str(current_position), 'General')
    selected_answer = attempt.answers.get(str(question.id), None)
    
    options = [
        {'label': 'A', 'text': question.option_a},
        {'label': 'B', 'text': question.option_b},
        {'label': 'C', 'text': question.option_c},
        {'label': 'D', 'text': question.option_d},
    ]
    
    context = {
        'attempt': attempt,
        'question': question,
        'options': options,
        'current_position': current_position,
        'total_questions': total_questions,
        'current_subject': current_subject,
        'selected_answer': selected_answer,
        'is_last': current_position == total_questions - 1,
        'progress': round(((current_position + 1) / total_questions) * 100, 1) if total_questions > 0 else 0,
        'answers_count': len(attempt.answers),
        'duration_minutes': 45,  # BECE default duration
    }
    return render(request, 'student_portal/take_bece_exam.html', context)

@login_required
def submit_bece_answer(request, attempt_id):
    """Submit BECE answer and go to next question"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    question_id = request.POST.get('question_id')
    answer = request.POST.get('answer')
    current_position = int(request.POST.get('current_position', 0))
    
    if question_id and answer:
        attempt.answers[question_id] = answer
        attempt.save()
    
    next_position = current_position + 1
    total_questions = len(request.session.get('bece_question_ids', []))
    
    if next_position >= total_questions:
        return redirect('student_portal:finish_bece_exam', attempt_id=attempt.id)
    
    return redirect(f"{reverse('student_portal:take_bece_exam_session', args=[attempt.id])}?q={next_position}")

@login_required
def finish_bece_exam(request, attempt_id):
    """Finish BECE exam"""
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    
    if attempt.status == 'COMPLETED':
        return redirect('student_portal:view_result', attempt_id=attempt.id)
    
    score = 0
    total_questions = attempt.total_questions
    
    for question_id, selected_answer in attempt.answers.items():
        try:
            question = Question.objects.get(id=int(question_id))
            if question.correct_answer == selected_answer:
                score += question.marks
        except Question.DoesNotExist:
            pass
    
    attempt.score = score
    attempt.status = 'COMPLETED'
    attempt.submitted_at = timezone.now()
    attempt.save()
    
    # Clear session
    request.session.pop('bece_attempt_id', None)
    request.session.pop('bece_question_ids', None)
    request.session.pop('bece_question_subject', None)
    request.session.pop('bece_total_questions', None)
    request.session.pop('bece_subjects', None)
    request.session.pop('bece_years', None)
    
    messages.success(request, f'✅ BECE completed! You scored {score}/{total_questions}')
    return redirect('student_portal:view_result', attempt_id=attempt.id)

@login_required
def quit_bece_exam(request, attempt_id):
    """Quit BECE exam"""
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    
    if attempt.status == 'COMPLETED':
        return redirect('student_portal:view_result', attempt_id=attempt.id)
    
    total_answered = len(attempt.answers)
    total_questions = attempt.total_questions
    
    # Calculate score so far
    score = 0
    for question_id, selected_answer in attempt.answers.items():
        try:
            question = Question.objects.get(id=int(question_id))
            if question.correct_answer == selected_answer:
                score += question.marks
        except Question.DoesNotExist:
            pass
    
    attempt.score = score
    attempt.status = 'COMPLETED'
    attempt.submitted_at = timezone.now()
    attempt.save()
    
    # Clear session
    request.session.pop('bece_attempt_id', None)
    request.session.pop('bece_question_ids', None)
    request.session.pop('bece_question_subject', None)
    request.session.pop('bece_total_questions', None)
    request.session.pop('bece_subjects', None)
    request.session.pop('bece_years', None)
    
    messages.info(request, f'BECE quit. You answered {total_answered}/{total_questions} questions.')
    return redirect('student_portal:view_result', attempt_id=attempt.id)

# ============================================================
# SCHOOL EXAM VIEWS
# ============================================================

@login_required
def school_exams_dashboard(request):
    """Show all available school exams (NORMAL) in a dashboard"""
    school_exams = Exam.objects.filter(
        category__iexact='NORMAL',
        is_active=True
    ).order_by('class_level', 'term')
    
    completed_exam_ids = StudentAttempt.objects.filter(
        student=request.user,
        status='COMPLETED'
    ).values_list('exam_id', flat=True)
    
    available_exams = school_exams.exclude(id__in=completed_exam_ids)
    
    grouped_exams = {}
    for exam in available_exams:
        level = exam.class_level or 'General'
        if level not in grouped_exams:
            grouped_exams[level] = []
        grouped_exams[level].append(exam)
    
    context = {
        'grouped_exams': grouped_exams,
        'total_exams': available_exams.count(),
    }
    return render(request, 'student_portal/school_exams_dashboard.html', context)

@login_required
def start_school_exam(request, exam_id):
    """Start a school exam (NORMAL) - creates attempt and redirects to take_exam"""
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    
    existing_attempt = StudentAttempt.objects.filter(
        student=request.user,
        exam=exam,
        status='IN_PROGRESS'
    ).first()
    
    if existing_attempt:
        attempt = existing_attempt
    else:
        completed = StudentAttempt.objects.filter(
            student=request.user,
            exam=exam,
            status='COMPLETED'
        ).exists()
        
        if completed:
            messages.warning(request, 'You have already completed this exam.')
            return redirect('student_portal:school_exams_dashboard')
        
        attempt = StudentAttempt.objects.create(
            student=request.user,
            exam=exam,
            total_questions=exam.questions.count(),
            answers={},
            status='IN_PROGRESS'
        )
    
    return redirect('student_portal:take_exam', attempt_id=attempt.id)

@login_required
def take_exam(request, attempt_id):
    """Take a school exam"""
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    exam = attempt.exam
    questions = exam.questions.all().order_by('question_number')
    
    total_questions = questions.count()
    current_position = int(request.GET.get('q', 0))
    
    if current_position >= total_questions:
        return redirect('student_portal:finish_exam', attempt_id=attempt.id)
    
    question = questions[current_position]
    selected_answer = attempt.answers.get(str(question.id), None)
    
    options = [
        {'label': 'A', 'text': question.option_a},
        {'label': 'B', 'text': question.option_b},
        {'label': 'C', 'text': question.option_c},
        {'label': 'D', 'text': question.option_d},
    ]
    
    context = {
        'attempt': attempt,
        'exam': exam,
        'question': question,
        'options': options,
        'current_position': current_position,
        'total_questions': total_questions,
        'selected_answer': selected_answer,
        'is_last': current_position == total_questions - 1,
        'progress': round(((current_position + 1) / total_questions) * 100, 1) if total_questions > 0 else 0,
        'answers_count': len(attempt.answers),
        'duration_minutes': exam.duration_minutes,
        'answers': json.dumps(attempt.answers),
    }
    return render(request, 'student_portal/take_exam.html', context)

@login_required
def submit_exam(request, attempt_id):
    """Submit school exam"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    question_id = request.POST.get('question_id')
    answer = request.POST.get('answer')
    current_position = int(request.POST.get('current_position', 0))
    answers_data = request.POST.get('answers', '{}')
    
    if question_id and answer:
        attempt.answers[question_id] = answer
        attempt.save()
    
    try:
        all_answers = json.loads(answers_data)
        for q_id, ans in all_answers.items():
            attempt.answers[q_id] = ans
        attempt.save()
    except:
        pass
    
    next_position = current_position + 1
    total_questions = attempt.total_questions
    
    if next_position >= total_questions:
        return redirect('student_portal:finish_exam', attempt_id=attempt.id)
    
    return redirect(f"{reverse('student_portal:take_exam', args=[attempt.id])}?q={next_position}")

@login_required
def finish_exam(request, attempt_id):
    """Finish school exam"""
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')
        
        if question_id and answer:
            attempt.answers[question_id] = answer
            attempt.save()
    
    if attempt.status == 'COMPLETED':
        return redirect('student_portal:view_result', attempt_id=attempt.id)
    
    score = 0
    total_questions = attempt.total_questions
    
    for question_id, selected_answer in attempt.answers.items():
        try:
            question = Question.objects.get(id=int(question_id))
            if question.correct_answer == selected_answer:
                score += question.marks
        except Question.DoesNotExist:
            pass
    
    attempt.score = score
    attempt.status = 'COMPLETED'
    attempt.submitted_at = timezone.now()
    attempt.save()
    
    messages.success(request, f'✅ Exam completed! You scored {score}/{total_questions}')
    return redirect('student_portal:view_result', attempt_id=attempt.id)

@login_required
def quit_exam(request, attempt_id):
    """Quit school exam"""
    attempt = get_object_or_404(StudentAttempt, id=attempt_id, student=request.user)
    
    if attempt.status == 'COMPLETED':
        return redirect('student_portal:view_result', attempt_id=attempt.id)
    
    score = 0
    total_answered = len(attempt.answers)
    total_questions = attempt.total_questions
    
    for question_id, selected_answer in attempt.answers.items():
        try:
            question = Question.objects.get(id=int(question_id))
            if question.correct_answer == selected_answer:
                score += question.marks
        except Question.DoesNotExist:
            pass
    
    attempt.score = score
    attempt.status = 'COMPLETED'
    attempt.submitted_at = timezone.now()
    attempt.save()
    
    messages.info(request, f'Exam quit. You answered {total_answered}/{total_questions} questions.')
    return redirect('student_portal:view_result', attempt_id=attempt.id)