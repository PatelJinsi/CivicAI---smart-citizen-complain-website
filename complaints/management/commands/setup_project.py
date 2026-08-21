"""
Management command: python manage.py setup_project
- Trains the AI model
- Creates departments
- Creates demo admin + citizen users
- Seeds sample complaints
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from complaints.models import Complaint, Department
from complaints.ai_engine import train_and_save_model, analyze_complaint


SAMPLE_COMPLAINTS = [
    {
        "title": "Large pothole on main road near Gandhi Market",
        "description": "There is a huge pothole on the main road near Gandhi Market. Several vehicles have been damaged. It has been there for more than 3 months. Very dangerous especially at night. Immediate repair required.",
        "location": "Gandhi Market, south bopal",
    },
    {
        "title": "Water leakage from municipal pipe on Station Road",
        "description": "A municipal water pipe has burst on Station Road near the bus stand. Water has been wasting continuously for the past 2 days. The road is flooded and difficult to cross. Please fix urgently.",
        "location": "Station Road, Vastrpur",
    },
    {
        "title": "Garbage not collected for 7 days in our colony",
        "description": "Garbage has not been collected from our colony for the past 7 days. The garbage bin is overflowing and rats have started appearing. The smell is unbearable. Residents are suffering from health issues.",
        "location": "Shivaji Nagar, Ambawadi",
    },
    {
        "title": "Street lights not working on entire road",
        "description": "All street lights on Nehru Road are not working for the past 5 days. The road is completely dark at night. Two bike accidents have already happened. Women feel unsafe. Please fix immediately.",
        "location": "Nehru Road, Near Park",
    },
    {
        "title": "Broken footpath causing accidents",
        "description": "The footpath on MG Road is completely broken with sharp edges. An elderly person fell yesterday and got injured. This has been reported before but no action taken. This is very negligent.",
        "location": "SG highway, near Nirvana party plot",
    },
    {
        "title": "No water supply for 3 days in entire area",
        "description": "There has been no water supply in our area for the last 3 days. We are buying water from private tankers at high cost. There are pregnant women and elderly people in our building who need water urgently.",
        "location": "Nikol gam ,Nikol",
    },
    {
        "title": "Illegal garbage dumping near school",
        "description": "People are illegally dumping garbage near the government school. Children have to walk past this dump every day. It is a health hazard. Stray dogs are gathering there. Please clean and put proper signs.",
        "location": "Government Primary School, Ambawadi",
    },
    {
        "title": "Electricity sparking wire hanging on road",
        "description": "A live electricity wire has been hanging low over the road after the storm 2 days ago. It is sparking when touched by vehicles. Very dangerous. A child narrowly escaped electrocution yesterday. URGENT!",
        "location": "Patel Chowk, Near Temple",
    },
    {
        "title": "Sewage water overflowing on road",
        "description": "The sewage drain near our society is blocked and sewage water is overflowing onto the road. Dirty water is entering homes. This is a serious health hazard. We have complained 3 times but no action.",
        "location": "Green Valley Society, Ambavadi",
    },
    {
        "title": "Road divider damaged causing accidents",
        "description": "The road divider on Ring Road was damaged in last month's storm and never repaired. Vehicles are crossing from wrong side causing head-on accidents. Please repair or at least put warning signs.",
        "location": "Ring Road, Near Flyover",
    },
    {
        "title": "Public dustbin broken and garbage scattered",
        "description": "The public dustbin near our colony gate has been broken for 2 weeks. Garbage is scattered all over the footpath. Dogs and birds are making it worse. Please replace the dustbin.",
        "location": "Sattelite road, oppo Kameshwar school",
    },
    {
        "title": "Dirty tap water causing illness",
        "description": "The municipal tap water in our area has been dirty brown color for the past 4 days. Many people in our building have fallen sick after drinking it. Please test the water quality and fix the pipeline.",
        "location": "Housing Board Colony, chanlodiya road",
    },
]


class Command(BaseCommand):
    help = 'Set up the project: train AI model, create users, seed sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🚀 Setting up CivicAI Project...\n'))

        # 1. Train AI Model
        self.stdout.write('🤖 Training AI model...')
        train_and_save_model()
        self.stdout.write(self.style.SUCCESS('   ✅ AI model trained and saved\n'))

        # 2. Create Departments
        self.stdout.write('🏛️  Creating departments...')
        departments = [
            ('Public Works Department', 'pwd@civicai.gov', 'Road and infrastructure'),
            ('Water Supply & Sewerage Board', 'water@civicai.gov', 'Water and drainage'),
            ('Municipal Sanitation Department', 'sanitation@civicai.gov', 'Garbage and sanitation'),
            ('Electricity Distribution Department', 'electricity@civicai.gov', 'Electricity and street lights'),
            ('General Administration Department', 'admin@civicai.gov', 'Other civic issues'),
        ]
        for name, email, desc in departments:
            Department.objects.get_or_create(name=name, defaults={'email': email, 'description': desc})
        self.stdout.write(self.style.SUCCESS('   ✅ 5 departments created\n'))

        # 3. Create Admin User
        self.stdout.write('👤 Creating admin user...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@civicai.gov',
                password='Admin@123',
                first_name='Admin',
                last_name='User',
            )
            self.stdout.write(self.style.SUCCESS('   ✅ Admin created: username=admin, password=Admin@123\n'))
        else:
            self.stdout.write('   ℹ️  Admin already exists\n')

        # 4. Create Demo Citizen
        self.stdout.write('👤 Creating demo citizen...')
        if not User.objects.filter(username='citizen1').exists():
            citizen = User.objects.create_user(
                username='citizen1',
                email='citizen@example.com',
                password='Citizen@123',
                first_name='Rahul',
                last_name='Sharma',
            )
        else:
            citizen = User.objects.get(username='citizen1')
            self.stdout.write('   ℹ️  Demo citizen already exists\n')

        # 5. Seed Sample Complaints with AI Analysis
        self.stdout.write('📋 Seeding sample complaints with AI analysis...')
        created = 0
        for data in SAMPLE_COMPLAINTS:
            if not Complaint.objects.filter(title=data['title']).exists():
                ai = analyze_complaint(data['title'], data['description'])
                dept, _ = Department.objects.get_or_create(name=ai['department_name'])
                statuses = ['new', 'new', 'in_progress', 'in_progress', 'resolved']
                Complaint.objects.create(
                    user=citizen,
                    title=data['title'],
                    description=data['description'],
                    location=data['location'],
                    category=ai['category'],
                    category_confidence=ai['category_confidence'],
                    urgency_score=ai['urgency_score'],
                    sentiment=ai['sentiment'],
                    department=dept,
                    status=random.choice(statuses),
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'   ✅ {created} sample complaints seeded\n'))

        # Done
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(self.style.SUCCESS('✅  Project setup complete!\n'))
        self.stdout.write('📌  Login credentials:')
        self.stdout.write('    Admin   → username: admin      | password: Admin@123')
        self.stdout.write('    Citizen → username: citizen1   | password: Citizen@123')
        self.stdout.write('\n🌐  Run: python manage.py runserver')
        self.stdout.write('    Then open: http://127.0.0.1:8000\n')