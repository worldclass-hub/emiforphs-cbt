from django.db import models
from django.conf import settings

class ExamCategory(models.TextChoices):
    BECE = 'BECE', 'BECE'
    NORMAL = 'NORMAL', 'Normal School'

class Subject(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=ExamCategory.choices)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    class Meta:
        unique_together = ['name', 'category']

class Exam(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=ExamCategory.choices)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    duration_minutes = models.IntegerField(default=120)
    instructions = models.TextField(blank=True)
    total_questions = models.IntegerField(default=0)
    
    # For NORMAL category only
    class_level = models.CharField(max_length=10, blank=True, null=True)
    term = models.CharField(max_length=20, blank=True, null=True)
    session = models.CharField(max_length=20, blank=True, null=True)
    
    # Who created it (for NORMAL exams)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='created_exams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.category == ExamCategory.NORMAL:
            return f"{self.title} ({self.class_level} - {self.term} Term)"
        return f"{self.title} ({self.category})"
    
    def update_total_questions(self):
        self.total_questions = self.questions.count()
        self.save()

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_number = models.IntegerField(default=1)
    text = models.TextField()
    
    # Options
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    
    # Correct answer
    CORRECT_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    correct_answer = models.CharField(max_length=1, choices=CORRECT_CHOICES)
    marks = models.IntegerField(default=1)
    
    # Year field for BECE
    year = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return f"Q{self.question_number}: {self.text[:50]}..."
    
    class Meta:
        ordering = ['question_number']
        unique_together = ['exam', 'question_number']

class StudentAttempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    answers = models.JSONField(default=dict)
    
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('TIMED_OUT', 'Timed Out'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='IN_PROGRESS')
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {self.status}"
    
    def percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 2)
    
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    def time_taken(self):
        if self.submitted_at and self.started_at:
            return self.submitted_at - self.started_at
        return None