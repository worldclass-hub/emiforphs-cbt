import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from exams.models import Subject, Exam, Question, ExamCategory
import time

class Command(BaseCommand):
    help = 'Import past questions from ALOC API'

    def add_arguments(self, parser):
        parser.add_argument('--subject', type=str, help='Subject name (e.g., chemistry)')
        parser.add_argument('--type', type=str, default='utme', help='Exam type: utme, wassce, postutme')
        parser.add_argument('--year', type=int, help='Specific year to import')
        parser.add_argument('--all', action='store_true', help='Import all subjects and years')
        parser.add_argument('--limit', type=int, default=100, help='Max questions per import')

    def handle(self, *args, **kwargs):
        subject = kwargs.get('subject')
        exam_type = kwargs.get('type')
        year = kwargs.get('year')
        import_all = kwargs.get('all')
        limit = kwargs.get('limit', 100)
        
        API_KEY = 'cd7c4420admshc43135a2cb98abcp1c4999jsnf919ce4bb78a'
        
        # ✅ CORRECT HEADERS - Using the ALOC host
        self.headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': 'questions.aloc.com.ng'
        }

        all_subjects = [
            'mathematics', 'english', 'physics', 'chemistry', 'biology',
            'economics', 'government', 'literature', 'geography', 'commerce',
            'accounting', 'history', 'french', 'yoruba', 'igbo', 'hausa'
        ]

        if import_all:
            self.stdout.write('🌱 Importing all subjects...')
            years = list(range(2000, 2017))
            total = 0
            for subj in all_subjects:
                for yr in years:
                    count = self.import_questions(subj, exam_type, yr, limit)
                    total += count
                    time.sleep(0.5)
            self.stdout.write(self.style.SUCCESS(f'✅ Done! Total: {total} questions imported'))
        elif subject and year:
            self.import_questions(subject, exam_type, year, limit)
        elif subject:
            self.import_questions(subject, exam_type, None, limit)
        else:
            self.stdout.write(self.style.ERROR('❌ Please specify --subject and --year, or use --all'))

    @transaction.atomic
    def import_questions(self, subject_name, exam_type, year, limit):
        self.stdout.write(f'📥 Fetching {exam_type} questions for {subject_name}...')

        # ✅ Use the ALOC endpoint with correct headers
        url = "https://questions.aloc.com.ng/api/v2/q"
        
        params = {
            'subject': subject_name,
            'type': exam_type,
        }
        if year:
            params['year'] = year

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get('questions', [])
                
                if not questions:
                    self.stdout.write(self.style.WARNING(f'⚠️ No questions found for {subject_name} {year or ""}'))
                    return 0
                
                # Save to database
                category = 'JAMB' if exam_type == 'utme' else 'WAEC' if exam_type == 'wassce' else 'BECE'
                subject, _ = Subject.objects.get_or_create(
                    name=subject_name.title(),
                    category=category
                )

                exam_title = f"{category} Past Questions: {subject_name.title()}"
                exam, created = Exam.objects.get_or_create(
                    title=exam_title,
                    category=category,
                    subject=subject,
                    defaults={
                        'duration_minutes': 45,
                        'is_active': True,
                        'instructions': f"{category} past questions for {subject_name.title()}"
                    }
                )

                if not created and year:
                    Question.objects.filter(exam=exam, year=str(year)).delete()

                count = 0
                for q_data in questions[:limit]:
                    year_value = q_data.get('year', str(year)) if year else q_data.get('year', '')
                    
                    question_text = q_data.get('question', 'No question text')
                    option_a = q_data.get('option_a', '')
                    option_b = q_data.get('option_b', '')
                    option_c = q_data.get('option_c', '')
                    option_d = q_data.get('option_d', '')
                    correct_answer = q_data.get('answer', 'A')
                    
                    Question.objects.create(
                        exam=exam,
                        question_number=q_data.get('id', count + 1),
                        text=question_text,
                        option_a=option_a,
                        option_b=option_b,
                        option_c=option_c,
                        option_d=option_d,
                        correct_answer=correct_answer,
                        year=str(year_value),
                        marks=1
                    )
                    count += 1

                exam.total_questions = Question.objects.filter(exam=exam).count()
                exam.save()

                self.stdout.write(self.style.SUCCESS(
                    f'✅ Imported {count} questions for {subject_name} {year or ""} ({category})'
                ))
                return count

            else:
                self.stdout.write(self.style.ERROR(
                    f'❌ API Error: {response.status_code} - {response.text[:200]}'
                ))
                return 0

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            return 0