from django.contrib import admin
from .models import Subject, Exam, Question, StudentAttempt

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5
    fields = ['question_number', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'marks']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'subject', 'duration_minutes', 'total_questions', 'is_active', 'created_at']
    list_filter = ['category', 'subject', 'is_active', 'class_level', 'term']
    search_fields = ['title', 'created_by__username']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'category', 'subject', 'duration_minutes', 'instructions')
        }),
        ('Normal School Only', {
            'fields': ('class_level', 'term', 'session', 'created_by'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_number', 'exam', 'text_preview', 'correct_answer', 'marks']
    list_filter = ['exam__category']
    search_fields = ['text', 'exam__title']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'

@admin.register(StudentAttempt)
class StudentAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'score', 'total_questions', 'percentage', 'status', 'started_at']
    list_filter = ['status', 'exam__category']
    search_fields = ['student__username', 'exam__title']
    readonly_fields = ['started_at', 'submitted_at']