from django.core.management.base import BaseCommand
from exams.models import Subject, Exam, Question, ExamCategory
import random

class Command(BaseCommand):
    help = 'Seed JAMB, WAEC, and BECE subjects with 20 questions each'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🌱 Starting to seed exams with 20 questions each...'))
        
        # Create subjects
        self.seed_subjects()
        
        # Create sample exams with 20 questions each
        self.seed_national_exams('JAMB', 45)
        self.seed_national_exams('WAEC', 60)
        self.seed_national_exams('BECE', 45)
        
        self.stdout.write(self.style.SUCCESS('✅ All exams seeded successfully with 20 questions each!'))

    def seed_subjects(self):
        """Create subjects for JAMB, WAEC, and BECE"""
        subjects_data = {
            'JAMB': [
                'English Language', 'Mathematics', 'Physics', 'Chemistry', 
                'Biology', 'Economics', 'Commerce', 'Accounting', 'Government',
                'Literature in English', 'History', 'Geography',
                'Christian Religious Studies', 'Islamic Religious Studies',
                'Yoruba', 'Igbo', 'Hausa', 'Arabic', 'French',
                'Agricultural Science', 'Further Mathematics', 'Civic Education',
                'Computer Studies', 'Data Processing'
            ],
            'WAEC': [
                'English Language', 'General Mathematics', 'Civic Education',
                'Physics', 'Chemistry', 'Biology', 'Further Mathematics',
                'Geography', 'Agricultural Science', 'Technical Drawing',
                'Literature in English', 'Government', 'History',
                'Christian Religious Studies', 'Islamic Religious Studies',
                'Yoruba', 'Igbo', 'Hausa', 'French', 'Arabic Studies',
                'Music', 'Fine Arts', 'Economics', 'Financial Accounting',
                'Commerce', 'Office Practice', 'Insurance', 'Marketing',
                'Bookkeeping', 'Data Processing'
            ],
            'BECE': [
                'English Language', 'Mathematics', 'Basic Science', 'Basic Technology',
                'Social Studies', 'Civic Education', 'Christian Religious Studies',
                'Islamic Religious Studies', 'Yoruba', 'Igbo', 'Hausa',
                'French Language', 'Information Technology', 'Computer Studies',
                'Agricultural Science', 'Home Economics', 'Fine Arts', 'Creative Arts',
                'Music', 'Physical Education', 'Business Studies', 'Introductory Technology',
                'Catering Craft Practice', 'Dyeing and Bleaching', 'Leather Work'
            ]
        }
        
        created_count = 0
        for category, subjects in subjects_data.items():
            for subject_name in subjects:
                subject, created = Subject.objects.get_or_create(
                    name=subject_name,
                    category=category
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✅ Created: {subject_name} ({category})')
        
        self.stdout.write(self.style.SUCCESS(f'📚 Created {created_count} new subjects'))

    def seed_national_exams(self, category, duration):
        """Seed exams for a specific category with 20 questions each"""
        subjects = Subject.objects.filter(category=category)
        
        for subject in subjects:
            exam_title = f"{category} Mock: {subject.name}"
            
            # Delete existing exam if it exists to refresh questions
            Exam.objects.filter(title=exam_title, category=category).delete()
            
            exam = Exam.objects.create(
                title=exam_title,
                category=category,
                subject=subject,
                duration_minutes=duration,
                instructions=f"This is a {category} mock exam for {subject.name}. Answer all 20 questions within the time limit.",
                is_active=True
            )
            
            # Generate 20 questions for this subject
            questions = self.get_questions_for_subject(subject.name, category)
            for i, q in enumerate(questions, 1):
                Question.objects.create(
                    exam=exam,
                    question_number=i,
                    text=q['text'],
                    option_a=q['options'][0],
                    option_b=q['options'][1],
                    option_c=q['options'][2],
                    option_d=q['options'][3],
                    correct_answer=q['correct'],
                    marks=1,
                    year=str(random.randint(2018, 2025))  # Random year between 2018-2025
                )
            
            exam.update_total_questions()
            self.stdout.write(f'  ✅ Created: {exam_title} with {exam.total_questions} questions')

    def get_questions_for_subject(self, subject_name, category):
        """Generate 20 questions for a specific subject"""
        
        # ============================================================
        # ENGLISH LANGUAGE QUESTIONS (20)
        # ============================================================
        if subject_name in ['English Language', 'English Language (Compulsory)']:
            return [
                {'text': 'Choose the word that is most nearly OPPOSITE in meaning to "BENEVOLENT"', 'options': ['Kind', 'Generous', 'Malevolent', 'Charitable'], 'correct': 'C'},
                {'text': 'Which of the following is a synonym for "ABUNDANT"?', 'options': ['Scarce', 'Plentiful', 'Rare', 'Limited'], 'correct': 'B'},
                {'text': 'Identify the correct spelling:', 'options': ['Accommadate', 'Accommodate', 'Acommodate', 'Accomodate'], 'correct': 'B'},
                {'text': 'Which word is an adjective?', 'options': ['Quickly', 'Beautiful', 'Run', 'Happily'], 'correct': 'B'},
                {'text': 'What is the plural of "Ox"?', 'options': ['Oxes', 'Oxen', 'Oxses', 'Oxens'], 'correct': 'B'},
                {'text': 'Choose the correct sentence:', 'options': ['He go to school', 'He goes to school', 'He going to school', 'He gone to school'], 'correct': 'B'},
                {'text': 'What is the past tense of "Run"?', 'options': ['Runned', 'Ran', 'Run', 'Runs'], 'correct': 'B'},
                {'text': 'Which is a pronoun?', 'options': ['Dog', 'He', 'Run', 'Beautiful'], 'correct': 'B'},
                {'text': 'What is the antonym of "Hot"?', 'options': ['Warm', 'Cold', 'Cool', 'Fire'], 'correct': 'B'},
                {'text': 'Choose the correct article: "___ apple"', 'options': ['A', 'An', 'The', 'None'], 'correct': 'B'},
                {'text': 'What is the comparative of "Good"?', 'options': ['Gooder', 'Better', 'Best', 'More good'], 'correct': 'B'},
                {'text': 'Which word is a verb?', 'options': ['Beautiful', 'Happiness', 'Jump', 'Quickly'], 'correct': 'C'},
                {'text': 'What is the plural of "Child"?', 'options': ['Childs', 'Children', 'Childrens', 'Childes'], 'correct': 'B'},
                {'text': 'Choose the correct preposition: "He is good ___ math"', 'options': ['In', 'At', 'On', 'For'], 'correct': 'B'},
                {'text': 'What is the synonym of "Happy"?', 'options': ['Sad', 'Joyful', 'Angry', 'Tired'], 'correct': 'B'},
                {'text': 'Which sentence is in past tense?', 'options': ['I eat rice', 'I ate rice', 'I am eating rice', 'I will eat rice'], 'correct': 'B'},
                {'text': 'What is the opposite of "Beautiful"?', 'options': ['Pretty', 'Ugly', 'Lovely', 'Cute'], 'correct': 'B'},
                {'text': 'Choose the correct conjunction: "I like tea ___ coffee"', 'options': ['But', 'And', 'Or', 'So'], 'correct': 'B'},
                {'text': 'What is the plural of "Mouse"?', 'options': ['Mouses', 'Mice', 'Mices', 'Mousies'], 'correct': 'B'},
                {'text': 'Which is a collective noun?', 'options': ['Dog', 'Team', 'Running', 'Beautiful'], 'correct': 'B'},
            ]

        # ============================================================
        # MATHEMATICS QUESTIONS (20)
        # ============================================================
        elif subject_name in ['Mathematics', 'General Mathematics', 'Maths']:
            return [
                {'text': 'What is 2 + 3 × 4?', 'options': ['20', '14', '24', '10'], 'correct': 'B'},
                {'text': 'What is the square root of 144?', 'options': ['11', '12', '13', '14'], 'correct': 'B'},
                {'text': 'What is 25% of 200?', 'options': ['25', '40', '50', '75'], 'correct': 'C'},
                {'text': 'What is the area of a rectangle with length 5 and width 3?', 'options': ['8', '10', '15', '20'], 'correct': 'C'},
                {'text': 'What is the sum of angles in a triangle?', 'options': ['90°', '180°', '270°', '360°'], 'correct': 'B'},
                {'text': 'What is 7 × 8?', 'options': ['48', '56', '64', '72'], 'correct': 'B'},
                {'text': 'What is the LCM of 4 and 6?', 'options': ['8', '10', '12', '14'], 'correct': 'C'},
                {'text': 'What is the square of 9?', 'options': ['72', '81', '90', '99'], 'correct': 'B'},
                {'text': 'What is the perimeter of a square with side 6cm?', 'options': ['24cm', '36cm', '48cm', '12cm'], 'correct': 'A'},
                {'text': 'What is 15 + 27?', 'options': ['40', '42', '44', '46'], 'correct': 'B'},
                {'text': 'What is 100 ÷ 4?', 'options': ['15', '20', '25', '30'], 'correct': 'C'},
                {'text': 'What is the GCF of 12 and 18?', 'options': ['4', '6', '8', '10'], 'correct': 'B'},
                {'text': 'What is 3³?', 'options': ['9', '18', '27', '36'], 'correct': 'C'},
                {'text': 'What is the diameter of a circle with radius 7?', 'options': ['7', '14', '21', '28'], 'correct': 'B'},
                {'text': 'What is 8 + 12 ÷ 4?', 'options': ['5', '8', '11', '14'], 'correct': 'C'},
                {'text': 'What is the square root of 81?', 'options': ['7', '8', '9', '10'], 'correct': 'C'},
                {'text': 'What is 45 - 28?', 'options': ['15', '17', '19', '21'], 'correct': 'B'},
                {'text': 'What is the product of 6 and 9?', 'options': ['48', '54', '60', '66'], 'correct': 'B'},
                {'text': 'What is 2³ + 3²?', 'options': ['11', '13', '15', '17'], 'correct': 'D'},
                {'text': 'What is the average of 4, 6, 8, 10?', 'options': ['5', '6', '7', '8'], 'correct': 'C'},
            ]

        # ============================================================
        # PHYSICS QUESTIONS (20)
        # ============================================================
        elif subject_name == 'Physics':
            return [
                {'text': 'What is the SI unit of force?', 'options': ['Joule', 'Newton', 'Watt', 'Pascal'], 'correct': 'B'},
                {'text': 'What is the speed of light approximately?', 'options': ['3×10⁸ m/s', '3×10⁶ m/s', '3×10¹⁰ m/s', '3×10⁴ m/s'], 'correct': 'A'},
                {'text': 'What is the acceleration due to gravity on Earth?', 'options': ['8.9 m/s²', '9.8 m/s²', '10.8 m/s²', '11.8 m/s²'], 'correct': 'B'},
                {'text': 'Which of the following is NOT a form of energy?', 'options': ['Kinetic', 'Potential', 'Magnetic', 'Newton'], 'correct': 'D'},
                {'text': 'What is the unit of electrical resistance?', 'options': ['Volt', 'Ampere', 'Ohm', 'Watt'], 'correct': 'C'},
                {'text': 'What is the formula for velocity?', 'options': ['v = d/t', 'v = t/d', 'v = d×t', 'v = a/t'], 'correct': 'A'},
                {'text': 'What is the boiling point of water in Kelvin?', 'options': ['273K', '373K', '473K', '573K'], 'correct': 'B'},
                {'text': 'Which is a conductor of electricity?', 'options': ['Rubber', 'Wood', 'Copper', 'Plastic'], 'correct': 'C'},
                {'text': 'What is the unit of power?', 'options': ['Joule', 'Newton', 'Watt', 'Volt'], 'correct': 'C'},
                {'text': 'What is the law of reflection?', 'options': ['Angle of incidence = Angle of reflection', 'Angle of incidence > Angle of reflection', 'Angle of incidence < Angle of reflection', 'No relationship'], 'correct': 'A'},
                {'text': 'What is the speed of sound in air approximately?', 'options': ['343 m/s', '440 m/s', '500 m/s', '600 m/s'], 'correct': 'A'},
                {'text': 'Which is a renewable source of energy?', 'options': ['Coal', 'Oil', 'Solar', 'Natural Gas'], 'correct': 'C'},
                {'text': 'What is the SI unit of pressure?', 'options': ['Newton', 'Pascal', 'Watt', 'Volt'], 'correct': 'B'},
                {'text': 'What is the formula for density?', 'options': ['d = m/v', 'd = v/m', 'd = m×v', 'd = a/v'], 'correct': 'A'},
                {'text': 'Which is an insulator?', 'options': ['Copper', 'Aluminum', 'Rubber', 'Iron'], 'correct': 'C'},
                {'text': 'What is the unit of frequency?', 'options': ['Hertz', 'Newton', 'Watt', 'Volt'], 'correct': 'A'},
                {'text': 'What is the law of conservation of energy?', 'options': ['Energy is created', 'Energy is destroyed', 'Energy cannot be created or destroyed', 'Energy can be created and destroyed'], 'correct': 'C'},
                {'text': 'What is the unit of work?', 'options': ['Newton', 'Joule', 'Watt', 'Volt'], 'correct': 'B'},
                {'text': 'Which is a type of wave?', 'options': ['Sound', 'Light', 'Water', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the speed of sound in water?', 'options': ['343 m/s', '500 m/s', '1500 m/s', '3000 m/s'], 'correct': 'C'},
            ]

        # ============================================================
        # CHEMISTRY QUESTIONS (20)
        # ============================================================
        elif subject_name == 'Chemistry':
            return [
                {'text': 'What is the chemical symbol for Gold?', 'options': ['Gd', 'Au', 'Ag', 'Go'], 'correct': 'B'},
                {'text': 'What is the atomic number of Carbon?', 'options': ['4', '6', '8', '10'], 'correct': 'B'},
                {'text': 'What is the chemical formula for water?', 'options': ['H₂O', 'CO₂', 'NaCl', 'HCl'], 'correct': 'A'},
                {'text': 'Which of the following is a noble gas?', 'options': ['Hydrogen', 'Oxygen', 'Neon', 'Chlorine'], 'correct': 'C'},
                {'text': 'What is the pH of pure water?', 'options': ['5', '6', '7', '8'], 'correct': 'C'},
                {'text': 'What is the chemical formula for salt?', 'options': ['H₂O', 'CO₂', 'NaCl', 'HCl'], 'correct': 'C'},
                {'text': 'What is the atomic number of Oxygen?', 'options': ['6', '8', '10', '12'], 'correct': 'B'},
                {'text': 'What is the chemical symbol for Silver?', 'options': ['Ag', 'Au', 'Fe', 'Cu'], 'correct': 'A'},
                {'text': 'What is the formula for sodium hydroxide?', 'options': ['NaOH', 'NaCl', 'Na₂O', 'NaH'], 'correct': 'A'},
                {'text': 'Which is an acid?', 'options': ['Sodium hydroxide', 'Hydrochloric acid', 'Salt', 'Water'], 'correct': 'B'},
                {'text': 'What is the chemical formula for carbon dioxide?', 'options': ['CO', 'CO₂', 'C₂O', 'C₂O₂'], 'correct': 'B'},
                {'text': 'What is the atomic number of Hydrogen?', 'options': ['1', '2', '3', '4'], 'correct': 'A'},
                {'text': 'What is the formula for sodium chloride?', 'options': ['NaOH', 'NaCl', 'Na₂O', 'NaH'], 'correct': 'B'},
                {'text': 'Which is a base?', 'options': ['Hydrochloric acid', 'Sodium hydroxide', 'Water', 'Salt'], 'correct': 'B'},
                {'text': 'What is the chemical symbol for Copper?', 'options': ['Co', 'Cu', 'Cp', 'C'], 'correct': 'B'},
                {'text': 'What is the atomic number of Nitrogen?', 'options': ['5', '7', '9', '11'], 'correct': 'B'},
                {'text': 'What is the formula for sulfuric acid?', 'options': ['HCl', 'H₂SO₄', 'HNO₃', 'CH₃COOH'], 'correct': 'B'},
                {'text': 'Which is a metal?', 'options': ['Oxygen', 'Gold', 'Sulfur', 'Carbon'], 'correct': 'B'},
                {'text': 'What is the chemical symbol for Iron?', 'options': ['Fe', 'Ir', 'In', 'Io'], 'correct': 'A'},
                {'text': 'What is the formula for ammonia?', 'options': ['NH₃', 'NH₄', 'N₂H₃', 'N₂H₄'], 'correct': 'A'},
            ]

        # ============================================================
        # BIOLOGY QUESTIONS (20)
        # ============================================================
        elif subject_name == 'Biology':
            return [
                {'text': 'What is the powerhouse of the cell?', 'options': ['Nucleus', 'Ribosome', 'Mitochondria', 'Golgi'], 'correct': 'C'},
                {'text': 'How many chromosomes do humans have?', 'options': ['44', '46', '48', '50'], 'correct': 'B'},
                {'text': 'What is the largest organ in the human body?', 'options': ['Liver', 'Heart', 'Brain', 'Skin'], 'correct': 'D'},
                {'text': 'Which of the following is NOT a type of blood vessel?', 'options': ['Artery', 'Vein', 'Capillary', 'Neuron'], 'correct': 'D'},
                {'text': 'What is the process by which plants make food?', 'options': ['Respiration', 'Photosynthesis', 'Transpiration', 'Germination'], 'correct': 'B'},
                {'text': 'What is the function of the heart?', 'options': ['To pump blood', 'To digest food', 'To filter waste', 'To produce hormones'], 'correct': 'A'},
                {'text': 'What is the largest organ in the body?', 'options': ['Liver', 'Skin', 'Brain', 'Heart'], 'correct': 'B'},
                {'text': 'Which is a type of white blood cell?', 'options': ['Red blood cell', 'Platelet', 'Lymphocyte', 'Plasma'], 'correct': 'C'},
                {'text': 'What is the function of the kidneys?', 'options': ['Pump blood', 'Digest food', 'Filter waste', 'Store bile'], 'correct': 'C'},
                {'text': 'What is the process of cell division?', 'options': ['Mitosis', 'Meiosis', 'Both', 'Neither'], 'correct': 'C'},
                {'text': 'What is the function of the lungs?', 'options': ['Pump blood', 'Exchange gases', 'Digest food', 'Filter waste'], 'correct': 'B'},
                {'text': 'Which is a type of joint?', 'options': ['Hinge', 'Pivot', 'Ball and socket', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the function of the stomach?', 'options': ['Pump blood', 'Exchange gases', 'Digest food', 'Filter waste'], 'correct': 'C'},
                {'text': 'What is the function of the liver?', 'options': ['Pump blood', 'Store bile', 'Digest food', 'Filter waste'], 'correct': 'B'},
                {'text': 'Which is a type of muscle?', 'options': ['Skeletal', 'Smooth', 'Cardiac', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the function of the pancreas?', 'options': ['Produce insulin', 'Pump blood', 'Digest food', 'Filter waste'], 'correct': 'A'},
                {'text': 'What is the function of the brain?', 'options': ['Control body functions', 'Pump blood', 'Digest food', 'Filter waste'], 'correct': 'A'},
                {'text': 'Which is a type of blood cell?', 'options': ['Red blood cell', 'White blood cell', 'Platelet', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the function of the skin?', 'options': ['Protect the body', 'Pump blood', 'Digest food', 'Filter waste'], 'correct': 'A'},
                {'text': 'What is the function of the reproductive system?', 'options': ['Produce offspring', 'Pump blood', 'Digest food', 'Filter waste'], 'correct': 'A'},
            ]

        # ============================================================
        # BASIC SCIENCE QUESTIONS (20)
        # ============================================================
        elif subject_name in ['Basic Science', 'Basic Science and Technology']:
            return [
                {'text': 'What is the boiling point of water?', 'options': ['80°C', '90°C', '100°C', '110°C'], 'correct': 'C'},
                {'text': 'Which is a renewable energy source?', 'options': ['Coal', 'Oil', 'Solar', 'Gas'], 'correct': 'C'},
                {'text': 'What is the largest planet?', 'options': ['Earth', 'Jupiter', 'Saturn', 'Mars'], 'correct': 'B'},
                {'text': 'What is the chemical symbol for Oxygen?', 'options': ['O', 'Ox', 'O₂', 'Om'], 'correct': 'A'},
                {'text': 'Which is a mammal?', 'options': ['Lizard', 'Whale', 'Crocodile', 'Snake'], 'correct': 'B'},
                {'text': 'What is the smallest planet?', 'options': ['Mercury', 'Venus', 'Earth', 'Mars'], 'correct': 'A'},
                {'text': 'What is the chemical symbol for Carbon?', 'options': ['Ca', 'C', 'Co', 'Cr'], 'correct': 'B'},
                {'text': 'Which is a bird?', 'options': ['Bat', 'Eagle', 'Butterfly', 'Frog'], 'correct': 'B'},
                {'text': 'What is the formula for water?', 'options': ['H₂O', 'CO₂', 'NaCl', 'HCl'], 'correct': 'A'},
                {'text': 'Which is a fish?', 'options': ['Whale', 'Shark', 'Dolphin', 'Turtle'], 'correct': 'B'},
                {'text': 'What is the chemical symbol for Hydrogen?', 'options': ['H', 'Hy', 'Hg', 'He'], 'correct': 'A'},
                {'text': 'Which is a reptile?', 'options': ['Crocodile', 'Frog', 'Butterfly', 'Eagle'], 'correct': 'A'},
                {'text': 'What is the chemical symbol for Nitrogen?', 'options': ['N', 'Ni', 'Ne', 'No'], 'correct': 'A'},
                {'text': 'Which is a type of rock?', 'options': ['Igneous', 'Sedimentary', 'Metamorphic', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the chemical symbol for Sodium?', 'options': ['So', 'Na', 'S', 'N'], 'correct': 'B'},
                {'text': 'Which is an insect?', 'options': ['Spider', 'Ant', 'Scorpion', 'Millipede'], 'correct': 'B'},
                {'text': 'What is the chemical symbol for Chlorine?', 'options': ['Cl', 'Ch', 'C', 'Cr'], 'correct': 'A'},
                {'text': 'Which is a type of soil?', 'options': ['Sandy', 'Clay', 'Loamy', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the chemical symbol for Iron?', 'options': ['Fe', 'Ir', 'In', 'Io'], 'correct': 'A'},
                {'text': 'Which is a type of energy?', 'options': ['Light', 'Sound', 'Heat', 'All of the above'], 'correct': 'D'},
            ]

        # ============================================================
        # SOCIAL STUDIES QUESTIONS (20)
        # ============================================================
        elif subject_name == 'Social Studies':
            return [
                {'text': 'What is the capital of Nigeria?', 'options': ['Lagos', 'Abuja', 'Ibadan', 'Kano'], 'correct': 'B'},
                {'text': 'Which is a social institution?', 'options': ['School', 'Market', 'Church', 'All of the above'], 'correct': 'D'},
                {'text': 'What is culture?', 'options': ['Food only', 'Dressing only', 'Total way of life', 'Religion only'], 'correct': 'C'},
                {'text': 'Which is a natural resource?', 'options': ['Oil', 'Water', 'Gas', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the population of Nigeria approximately?', 'options': ['100 million', '150 million', '200+ million', '50 million'], 'correct': 'C'},
                {'text': 'What is the currency of Nigeria?', 'options': ['Dollar', 'Pound', 'Naira', 'Euro'], 'correct': 'C'},
                {'text': 'How many states does Nigeria have?', 'options': ['30', '34', '36', '40'], 'correct': 'C'},
                {'text': 'What is the colors of the Nigerian flag?', 'options': ['Red, White, Blue', 'Green, White, Green', 'Red, Gold, Green', 'Blue, White, Blue'], 'correct': 'B'},
                {'text': 'What is the largest ethnic group in Nigeria?', 'options': ['Yoruba', 'Igbo', 'Hausa', 'Fulani'], 'correct': 'C'},
                {'text': 'What is the form of government in Nigeria?', 'options': ['Monarchy', 'Dictatorship', 'Democracy', 'Communism'], 'correct': 'C'},
                {'text': 'What is the official language of Nigeria?', 'options': ['English', 'French', 'Yoruba', 'Hausa'], 'correct': 'A'},
                {'text': 'What is the highest court in Nigeria?', 'options': ['Court of Appeal', 'Supreme Court', 'Federal Court', 'High Court'], 'correct': 'B'},
                {'text': 'Who is the Commander-in-Chief of the Nigerian Armed Forces?', 'options': ['Chief of Army Staff', 'President', 'Defence Minister', 'Chief of Defence Staff'], 'correct': 'B'},
                {'text': 'What is the legislative arm of government called?', 'options': ['Executive', 'Judiciary', 'Legislature', 'Civil Service'], 'correct': 'C'},
                {'text': 'What is the executive arm of government?', 'options': ['President', 'Supreme Court', 'National Assembly', 'Civil Service'], 'correct': 'A'},
                {'text': 'What is the judiciary?', 'options': ['President', 'Supreme Court', 'National Assembly', 'Civil Service'], 'correct': 'B'},
                {'text': 'What is the system of government in Nigeria?', 'options': ['Unitary', 'Federal', 'Confederal', 'None'], 'correct': 'B'},
                {'text': 'What is the role of the police?', 'options': ['Make laws', 'Interpret laws', 'Enforce laws', 'None'], 'correct': 'C'},
                {'text': 'What is the role of the military?', 'options': ['Defend the country', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the media?', 'options': ['Inform the public', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
            ]

        # ============================================================
        # CIVIC EDUCATION QUESTIONS (20)
        # ============================================================
        elif subject_name == 'Civic Education':
            return [
                {'text': 'What is the supreme law of Nigeria?', 'options': ['Constitution', 'Bill of Rights', 'Criminal Code', 'Civil Code'], 'correct': 'A'},
                {'text': 'How many states does Nigeria have?', 'options': ['30', '34', '36', '40'], 'correct': 'C'},
                {'text': 'What are the colors of the Nigerian flag?', 'options': ['Red, White, Blue', 'Green, White, Green', 'Red, Gold, Green', 'Blue, White, Blue'], 'correct': 'B'},
                {'text': 'Who is the Commander-in-Chief of the Armed Forces?', 'options': ['Chief of Army Staff', 'President', 'Defence Minister', 'Chief of Defence Staff'], 'correct': 'B'},
                {'text': 'What is the legislative arm of government?', 'options': ['Executive', 'Judiciary', 'Legislature', 'Civil Service'], 'correct': 'C'},
                {'text': 'What is the fundamental human right?', 'options': ['Right to life', 'Right to education', 'Right to freedom of speech', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the function of the executive arm?', 'options': ['Make laws', 'Interpret laws', 'Implement laws', 'None'], 'correct': 'C'},
                {'text': 'What is the function of the judiciary?', 'options': ['Make laws', 'Interpret laws', 'Implement laws', 'None'], 'correct': 'B'},
                {'text': 'What is the difference between the Nigerian flag and other flags?', 'options': ['Colors', 'Design', 'Symbolism', 'All of the above'], 'correct': 'D'},
                {'text': 'What is the National Anthem of Nigeria?', 'options': ['Arise O Compatriots', 'Nigeria We Hail Thee', 'God Save the Queen', 'None'], 'correct': 'A'},
                {'text': 'What is the National Pledge?', 'options': ['I pledge to Nigeria', 'I pledge to my country', 'I pledge allegiance', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the National Assembly?', 'options': ['Make laws', 'Implement laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the President?', 'options': ['Make laws', 'Implement laws', 'Interpret laws', 'None'], 'correct': 'B'},
                {'text': 'What is the role of the Supreme Court?', 'options': ['Make laws', 'Implement laws', 'Interpret laws', 'None'], 'correct': 'C'},
                {'text': 'What is the National Population Commission?', 'options': ['Count people', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the Independent National Electoral Commission (INEC)?', 'options': ['Conduct elections', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the Economic and Financial Crimes Commission (EFCC)?', 'options': ['Fight corruption', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the National Youth Service Corps (NYSC)?', 'options': ['Youth mobilization', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the police in Nigeria?', 'options': ['Maintain law and order', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the military?', 'options': ['Defend the country', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
            ]

        # ============================================================
        # ECONOMICS QUESTIONS (20)
        # ============================================================
        elif subject_name == 'Economics':
            return [
                {'text': 'What is the basic economic problem?', 'options': ['Scarcity', 'Inflation', 'Unemployment', 'Poverty'], 'correct': 'A'},
                {'text': 'What is the law of demand?', 'options': ['Price up, Demand up', 'Price up, Demand down', 'Price down, Demand down', 'No relationship'], 'correct': 'B'},
                {'text': 'What is GDP?', 'options': ['Gross Domestic Product', 'Gross National Product', 'Gross Development Product', 'Global Domestic Product'], 'correct': 'A'},
                {'text': 'Which is NOT a factor of production?', 'options': ['Land', 'Labor', 'Capital', 'Money'], 'correct': 'D'},
                {'text': 'What is inflation?', 'options': ['Increase in money supply', 'Decrease in prices', 'Increase in general price level', 'Decrease in money supply'], 'correct': 'C'},
                {'text': 'What is a market?', 'options': ['A place where goods are bought and sold', 'A place to eat', 'A place to sleep', 'None'], 'correct': 'A'},
                {'text': 'What is demand?', 'options': ['Quantity of goods consumers are willing to buy', 'Quantity of goods producers are willing to sell', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is supply?', 'options': ['Quantity of goods consumers are willing to buy', 'Quantity of goods producers are willing to sell', 'Both', 'None'], 'correct': 'B'},
                {'text': 'What is the law of supply?', 'options': ['Price up, Supply up', 'Price up, Supply down', 'Price down, Supply up', 'No relationship'], 'correct': 'A'},
                {'text': 'What is a monopoly?', 'options': ['Many sellers', 'One seller', 'Two sellers', 'No sellers'], 'correct': 'B'},
                {'text': 'What is an oligopoly?', 'options': ['Many sellers', 'One seller', 'Few sellers', 'No sellers'], 'correct': 'C'},
                {'text': 'What is perfect competition?', 'options': ['Many sellers', 'One seller', 'Few sellers', 'No sellers'], 'correct': 'A'},
                {'text': 'What is GNP?', 'options': ['Gross National Product', 'Gross Domestic Product', 'Gross Development Product', 'Global National Product'], 'correct': 'A'},
                {'text': 'What is the Central Bank of Nigeria?', 'options': ['First Bank', 'Access Bank', 'CBN', 'Union Bank'], 'correct': 'C'},
                {'text': 'What is the currency of Nigeria?', 'options': ['Dollar', 'Pound', 'Naira', 'Euro'], 'correct': 'C'},
                {'text': 'What is a budget deficit?', 'options': ['Expenditure > Revenue', 'Revenue > Expenditure', 'Revenue = Expenditure', 'None'], 'correct': 'A'},
                {'text': 'What is a budget surplus?', 'options': ['Expenditure > Revenue', 'Revenue > Expenditure', 'Revenue = Expenditure', 'None'], 'correct': 'B'},
                {'text': 'What is the balance of trade?', 'options': ['Exports - Imports', 'Imports - Exports', 'Exports + Imports', 'None'], 'correct': 'A'},
                {'text': 'What is GDP per capita?', 'options': ['GDP / Population', 'Population / GDP', 'GDP × Population', 'None'], 'correct': 'A'},
                {'text': 'What is unemployment?', 'options': ['People without jobs', 'People with jobs', 'People in school', 'None'], 'correct': 'A'},
            ]

        # ============================================================
        # GOVERNMENT QUESTIONS (20)
        # ============================================================
        elif subject_name == 'Government':
            return [
                {'text': 'What is the highest court in Nigeria?', 'options': ['Court of Appeal', 'Supreme Court', 'Federal Court', 'High Court'], 'correct': 'B'},
                {'text': 'How many states does Nigeria have?', 'options': ['30', '34', '36', '40'], 'correct': 'C'},
                {'text': 'What is the color of the Nigerian flag?', 'options': ['Red, White, Blue', 'Green, White, Green', 'Red, Gold, Green', 'Blue, White, Blue'], 'correct': 'B'},
                {'text': 'Who is the Commander-in-Chief of the Nigerian Armed Forces?', 'options': ['Chief of Army Staff', 'President', 'Defence Minister', 'Chief of Defence Staff'], 'correct': 'B'},
                {'text': 'What is the legislative arm of government called?', 'options': ['Executive', 'Judiciary', 'Legislature', 'Civil Service'], 'correct': 'C'},
                {'text': 'What is the executive arm of government?', 'options': ['President', 'Supreme Court', 'National Assembly', 'Civil Service'], 'correct': 'A'},
                {'text': 'What is the judiciary?', 'options': ['President', 'Supreme Court', 'National Assembly', 'Civil Service'], 'correct': 'B'},
                {'text': 'What is the system of government in Nigeria?', 'options': ['Unitary', 'Federal', 'Confederal', 'None'], 'correct': 'B'},
                {'text': 'What is the role of the police?', 'options': ['Make laws', 'Interpret laws', 'Enforce laws', 'None'], 'correct': 'C'},
                {'text': 'What is the role of the military?', 'options': ['Defend the country', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the National Assembly?', 'options': ['The Senate and House of Representatives', 'The Supreme Court', 'The Presidency', 'None'], 'correct': 'A'},
                {'text': 'How many senators does Nigeria have?', 'options': ['109', '120', '130', '140'], 'correct': 'A'},
                {'text': 'How many members of the House of Representatives?', 'options': ['360', '370', '380', '390'], 'correct': 'A'},
                {'text': 'What is the local government?', 'options': ['Third tier of government', 'First tier', 'Second tier', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the INEC?', 'options': ['Conduct elections', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the EFCC?', 'options': ['Fight corruption', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the ICPC?', 'options': ['Fight corruption', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the Code of Conduct Bureau?', 'options': ['Asset declaration', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the Federal Character Commission?', 'options': ['Ensure federal character', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
                {'text': 'What is the role of the National Youth Service Corps (NYSC)?', 'options': ['Youth mobilization', 'Make laws', 'Interpret laws', 'None'], 'correct': 'A'},
            ]

        # ============================================================
        # BASIC TECHNOLOGY QUESTIONS (20)
        # ============================================================
        elif subject_name in ['Basic Technology', 'Introductory Technology']:
            return [
                {'text': 'What is a computer?', 'options': ['Electronic device that processes data', 'Mechanical device', 'Electrical device', 'None'], 'correct': 'A'},
                {'text': 'What is the CPU?', 'options': ['Central Processing Unit', 'Central Power Unit', 'Computer Processing Unit', 'None'], 'correct': 'A'},
                {'text': 'What is a monitor?', 'options': ['Output device', 'Input device', 'Storage device', 'None'], 'correct': 'A'},
                {'text': 'What is a keyboard?', 'options': ['Input device', 'Output device', 'Storage device', 'None'], 'correct': 'A'},
                {'text': 'What is a mouse?', 'options': ['Input device', 'Output device', 'Storage device', 'None'], 'correct': 'A'},
                {'text': 'What is a printer?', 'options': ['Output device', 'Input device', 'Storage device', 'None'], 'correct': 'A'},
                {'text': 'What is a hard drive?', 'options': ['Storage device', 'Input device', 'Output device', 'None'], 'correct': 'A'},
                {'text': 'What is software?', 'options': ['Programs that run on a computer', 'Hardware devices', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is hardware?', 'options': ['Physical parts of a computer', 'Programs', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a network?', 'options': ['Connected computers', 'Standalone computers', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is the internet?', 'options': ['Global network of networks', 'Local network', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a website?', 'options': ['Web pages on the internet', 'Computer programs', 'Hardware devices', 'None'], 'correct': 'A'},
                {'text': 'What is an email?', 'options': ['Electronic mail', 'Paper mail', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a virus?', 'options': ['Malicious software', 'Hardware device', 'Computer program', 'None'], 'correct': 'A'},
                {'text': 'What is an antivirus?', 'options': ['Software that protects against viruses', 'Hardware device', 'Computer program', 'None'], 'correct': 'A'},
                {'text': 'What is a backup?', 'options': ['Copy of data', 'Delete data', 'Modify data', 'None'], 'correct': 'A'},
                {'text': 'What is a database?', 'options': ['Organized collection of data', 'Random collection of data', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a spreadsheet?', 'options': ['Program for calculations', 'Word processing program', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a word processor?', 'options': ['Program for typing documents', 'Program for calculations', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a presentation software?', 'options': ['Program for presentations', 'Program for calculations', 'Both', 'None'], 'correct': 'A'},
            ]

        # ============================================================
        # INFORMATION TECHNOLOGY / COMPUTER STUDIES (20)
        # ============================================================
        elif subject_name in ['Information Technology', 'Computer Studies', 'Data Processing']:
            return [
                {'text': 'What is a computer?', 'options': ['Electronic device that processes data', 'Mechanical device', 'Electrical device', 'None'], 'correct': 'A'},
                {'text': 'What is the CPU?', 'options': ['Central Processing Unit', 'Central Power Unit', 'Computer Processing Unit', 'None'], 'correct': 'A'},
                {'text': 'What is an operating system?', 'options': ['Software that manages hardware', 'Hardware device', 'Computer program', 'None'], 'correct': 'A'},
                {'text': 'What is RAM?', 'options': ['Random Access Memory', 'Read Access Memory', 'Run Access Memory', 'None'], 'correct': 'A'},
                {'text': 'What is ROM?', 'options': ['Read Only Memory', 'Random Only Memory', 'Run Only Memory', 'None'], 'correct': 'A'},
                {'text': 'What is a keyboard?', 'options': ['Input device', 'Output device', 'Storage device', 'None'], 'correct': 'A'},
                {'text': 'What is a mouse?', 'options': ['Input device', 'Output device', 'Storage device', 'None'], 'correct': 'A'},
                {'text': 'What is a printer?', 'options': ['Output device', 'Input device', 'Storage device', 'None'], 'correct': 'A'},
                {'text': 'What is a hard drive?', 'options': ['Storage device', 'Input device', 'Output device', 'None'], 'correct': 'A'},
                {'text': 'What is software?', 'options': ['Programs that run on a computer', 'Hardware devices', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is hardware?', 'options': ['Physical parts of a computer', 'Programs', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a network?', 'options': ['Connected computers', 'Standalone computers', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is the internet?', 'options': ['Global network of networks', 'Local network', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a website?', 'options': ['Web pages on the internet', 'Computer programs', 'Hardware devices', 'None'], 'correct': 'A'},
                {'text': 'What is an email?', 'options': ['Electronic mail', 'Paper mail', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is a virus?', 'options': ['Malicious software', 'Hardware device', 'Computer program', 'None'], 'correct': 'A'},
                {'text': 'What is an antivirus?', 'options': ['Software that protects against viruses', 'Hardware device', 'Computer program', 'None'], 'correct': 'A'},
                {'text': 'What is a backup?', 'options': ['Copy of data', 'Delete data', 'Modify data', 'None'], 'correct': 'A'},
                {'text': 'What is a database?', 'options': ['Organized collection of data', 'Random collection of data', 'Both', 'None'], 'correct': 'A'},
                {'text': 'What is data processing?', 'options': ['Collecting and processing data', 'Deleting data', 'Ignoring data', 'None'], 'correct': 'A'},
            ]

        # ============================================================
        # DEFAULT: GENERIC QUESTIONS (20)
        # ============================================================
        else:
            return [
                {'text': f'Sample question 1 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'A'},
                {'text': f'Sample question 2 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'B'},
                {'text': f'Sample question 3 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'C'},
                {'text': f'Sample question 4 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'D'},
                {'text': f'Sample question 5 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'A'},
                {'text': f'Sample question 6 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'B'},
                {'text': f'Sample question 7 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'C'},
                {'text': f'Sample question 8 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'D'},
                {'text': f'Sample question 9 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'A'},
                {'text': f'Sample question 10 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'B'},
                {'text': f'Sample question 11 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'C'},
                {'text': f'Sample question 12 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'D'},
                {'text': f'Sample question 13 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'A'},
                {'text': f'Sample question 14 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'B'},
                {'text': f'Sample question 15 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'C'},
                {'text': f'Sample question 16 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'D'},
                {'text': f'Sample question 17 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'A'},
                {'text': f'Sample question 18 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'B'},
                {'text': f'Sample question 19 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'C'},
                {'text': f'Sample question 20 for {subject_name}', 'options': ['Option A', 'Option B', 'Option C', 'Option D'], 'correct': 'D'},
            ]