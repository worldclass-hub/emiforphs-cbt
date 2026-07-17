from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.urls import reverse
from .models import CustomUser, Role
from exams.models import StudentAttempt

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'STUDENT')
        
        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return render(request, 'accounts/register.html', {'roles': Role.choices})
        
        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'accounts/register.html', {'roles': Role.choices})
        
        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role
        )
        
        # Log the user in
        login(request, user)
        messages.success(request, f'Welcome {first_name} {last_name}! You are registered as a {role}.')
        return redirect('dashboard')
    
    return render(request, 'accounts/register.html', {'roles': Role.choices})

@login_required
def dashboard(request):
    """Dashboard with role-based stats"""
    user = request.user
    context = {'role': user.role}
    
    # ============================================================
    # ACTIVE EXAM DETECTION - For warning system (School Exams only)
    # ============================================================
    has_active_exam = False
    active_exam_id = None
    active_exam_type = None
    active_exam_url = None
    
    if user.role == 'STUDENT':
        # Check for active StudentAttempt (school exams)
        active_attempt = StudentAttempt.objects.filter(
            student=user,
            status='IN_PROGRESS'
        ).first()
        
        if active_attempt:
            has_active_exam = True
            active_exam_id = active_attempt.id
            active_exam_type = 'attempt'
            active_exam_url = reverse('student_portal:take_exam', args=[active_attempt.id])
    
    # Add to context
    context.update({
        'has_active_exam': has_active_exam,
        'active_exam_id': active_exam_id,
        'active_exam_type': active_exam_type,
        'active_exam_url': active_exam_url,
    })
    
    # ============================================================
    # STUDENT STATS
    # ============================================================
    if user.role == 'STUDENT':
        # Get all completed attempts (StudentAttempt only)
        attempts = StudentAttempt.objects.filter(
            student=user,
            status='COMPLETED'
        )
        
        # Calculate stats
        exams_taken = attempts.count()
        
        # Calculate average score
        all_scores = []
        for a in attempts:
            if a.total_questions > 0:
                all_scores.append((a.score / a.total_questions) * 100)
        
        avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        
        # Best score
        best_score = round(max(all_scores), 1) if all_scores else 0
        
        # Rank (count how many students have higher avg score)
        all_students_scores = []
        for student in CustomUser.objects.filter(role='STUDENT'):
            student_attempts = StudentAttempt.objects.filter(
                student=student,
                status='COMPLETED'
            )
            student_scores = []
            for a in student_attempts:
                if a.total_questions > 0:
                    student_scores.append((a.score / a.total_questions) * 100)
            if student_scores:
                all_students_scores.append({
                    'student': student,
                    'avg': sum(student_scores) / len(student_scores)
                })
        
        # Sort by avg score descending
        all_students_scores.sort(key=lambda x: x['avg'], reverse=True)
        
        # Find current user's rank
        rank = 1
        for idx, data in enumerate(all_students_scores, 1):
            if data['student'].id == user.id:
                rank = idx
                break
        
        context.update({
            'exams_taken': exams_taken,
            'avg_score': avg_score,
            'best_score': best_score,
            'rank': rank,
        })
    
    # ============================================================
    # TEACHER STATS
    # ============================================================
    elif user.role == 'TEACHER':
        from exams.models import Exam
        
        total_exams = Exam.objects.filter(created_by=user).count()
        # Count students who have taken the teacher's exams
        exam_ids = Exam.objects.filter(created_by=user).values_list('id', flat=True)
        students_count = StudentAttempt.objects.filter(
            exam_id__in=exam_ids,
            status='COMPLETED'
        ).values('student').distinct().count()
        
        # Avg score for teacher's exams
        attempts = StudentAttempt.objects.filter(
            exam_id__in=exam_ids,
            status='COMPLETED'
        )
        avg_score = 0
        if attempts.exists():
            total_percentages = []
            for a in attempts:
                if a.total_questions > 0:
                    total_percentages.append((a.score / a.total_questions) * 100)
            avg_score = round(sum(total_percentages) / len(total_percentages), 1) if total_percentages else 0
        
        pending = StudentAttempt.objects.filter(
            exam_id__in=exam_ids,
            status='IN_PROGRESS'
        ).count()
        
        context.update({
            'total_exams': total_exams,
            'students_count': students_count,
            'avg_score': avg_score,
            'pending': pending,
        })
    
    # ============================================================
    # ADMIN STATS
    # ============================================================
    elif user.role == 'ADMIN':
        from exams.models import Exam
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        total_users = User.objects.count()
        total_exams = Exam.objects.count()
        active_students = User.objects.filter(role='STUDENT', is_active=True).count()
        
        # Pass rate (all completed attempts)
        all_attempts = StudentAttempt.objects.filter(status='COMPLETED')
        
        passed = 0
        total = 0
        for a in all_attempts:
            total += 1
            if a.total_questions > 0 and (a.score / a.total_questions) * 100 >= 70:
                passed += 1
        
        pass_rate = round((passed / total) * 100, 1) if total > 0 else 0
        
        context.update({
            'total_users': total_users,
            'total_exams': total_exams,
            'active_students': active_students,
            'pass_rate': pass_rate,
        })
    
    return render(request, 'accounts/dashboard.html', context)