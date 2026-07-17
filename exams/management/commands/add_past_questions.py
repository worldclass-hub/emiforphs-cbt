import csv
import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from exams.models import Subject, Exam, Question, ExamCategory

class Command(BaseCommand):
    help = 'Manually add past questions from CSV or JSON file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to CSV or JSON file')
        parser.add_argument('--subject', type=str, help='Subject name (e.g., Government)')
        parser.add_argument('--year', type=int, help='Year of exam (e.g., 2023)')
        parser.add_argument('--type', type=str, default='JAMB', help='Exam type: JAMB, WAEC, BECE')
        parser.add_argument('--all', action='store_true', help='Import all CSV files in the data folder')

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('file')
        subject_name = kwargs.get('subject')
        year = kwargs.get('year')
        exam_type = kwargs.get('type').upper()
        import_all = kwargs.get('all')

        if import_all:
            self.import_all_files()
            return

        if not file_path or not subject_name:
            self.stdout.write(self.style.ERROR('❌ Please provide --file and --subject'))
            self.stdout.write('Example: python manage.py add_past_questions --file questions.csv --subject Government --year 2023 --type JAMB')
            return

        self.import_single_file(file_path, subject_name, year, exam_type)

    def import_single_file(self, file_path, subject_name, year, exam_type):
        """Import a single CSV file"""
        self.stdout.write(f'📥 Importing: {file_path}')
        
        # Get or create subject
        subject, created = Subject.objects.get_or_create(
            name=subject_name.title(),
            category=exam_type
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created subject: {subject_name} ({exam_type})'))

        # Get or create exam
        exam_title = f"{exam_type} Past Questions: {subject_name.title()}"
        exam, created = Exam.objects.get_or_create(
            title=exam_title,
            category=exam_type,
            subject=subject,
            defaults={
                'duration_minutes': 45,
                'is_active': True,
                'instructions': f"{exam_type} past questions for {subject_name.title()}"
            }
        )

        # Delete existing questions for this subject/year if year provided
        if year:
            deleted = Question.objects.filter(exam=exam, year=str(year)).delete()
            self.stdout.write(f'🗑️ Deleted {deleted[0]} existing questions for {subject_name} ({year})')

        # Import questions
        count = 0
        if file_path.endswith('.csv'):
            count = self.import_csv(file_path, exam, year)
        elif file_path.endswith('.json'):
            count = self.import_json(file_path, exam, year)
        else:
            self.stdout.write(self.style.ERROR('❌ Unsupported file format. Use CSV or JSON.'))
            return

        exam.total_questions = Question.objects.filter(exam=exam).count()
        exam.save()

        self.stdout.write(self.style.SUCCESS(
            f'✅ Imported {count} questions for {subject_name} {year or "all years"} ({exam_type})'
        ))

    def import_all_files(self):
        """Import all CSV files from the data folder"""
        data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR('❌ No "data" folder found. Create one and add CSV files.'))
            return

        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not csv_files:
            self.stdout.write(self.style.WARNING('⚠️ No CSV files found in data folder.'))
            return

        self.stdout.write(f'📥 Found {len(csv_files)} CSV files to import...')
        
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            # Extract subject name from filename (e.g., "government_2023.csv" -> "Government")
            base_name = os.path.splitext(csv_file)[0]
            parts = base_name.split('_')
            subject_name = parts[0].title() if parts else base_name.title()
            year = int(parts[1]) if len(parts) > 1 else None
            
            self.import_single_file(file_path, subject_name, year, 'JAMB')

    def import_csv(self, file_path, exam, year):
        """Import questions from CSV file"""
        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Question.objects.create(
                    exam=exam,
                    question_number=count + 1,
                    text=row.get('question', 'No question'),
                    option_a=row.get('option_a', ''),
                    option_b=row.get('option_b', ''),
                    option_c=row.get('option_c', ''),
                    option_d=row.get('option_d', ''),
                    correct_answer=row.get('correct_answer', 'A').upper(),
                    year=str(year or row.get('year', '')),
                    marks=1
                )
                count += 1
        return count

    def import_json(self, file_path, exam, year):
        """Import questions from JSON file"""
        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data.get('questions', data if isinstance(data, list) else [])
            for q_data in questions:
                Question.objects.create(
                    exam=exam,
                    question_number=count + 1,
                    text=q_data.get('question', q_data.get('text', 'No question')),
                    option_a=q_data.get('option_a', q_data.get('a', '')),
                    option_b=q_data.get('option_b', q_data.get('b', '')),
                    option_c=q_data.get('option_c', q_data.get('c', '')),
                    option_d=q_data.get('option_d', q_data.get('d', '')),
                    correct_answer=q_data.get('correct_answer', q_data.get('answer', 'A')).upper(),
                    year=str(year or q_data.get('year', '')),
                    marks=1
                )
                count += 1
        return count