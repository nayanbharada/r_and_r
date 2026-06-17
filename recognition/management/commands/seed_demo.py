from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recognition.models import EmployeeProfile, Recognition, RewardItem


class Command(BaseCommand):
    help = 'Create demo employees and sample recognition activity.'

    def handle(self, *args, **options):
        User = get_user_model()
        employees = [
            ('nayan', 'Nayan', 'Shah', 'Energy', 'Plant Engineer', EmployeeProfile.Role.ADMIN),
            ('aisha', 'Aisha', 'Mehta', 'Digital', 'Product Manager', EmployeeProfile.Role.STAFF),
            ('rahul', 'Rahul', 'Verma', 'Ports', 'Operations Lead', EmployeeProfile.Role.STAFF),
            ('priya', 'Priya', 'Iyer', 'Finance', 'Analyst', EmployeeProfile.Role.EMPLOYEE),
            ('kabir', 'Kabir', 'Rao', 'Green Energy', 'Safety Champion', EmployeeProfile.Role.EMPLOYEE),
        ]

        profiles = []
        for index, (username, first, last, department, designation, role) in enumerate(employees, 1):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{username}@adani.example',
                },
            )
            user.email = f'{username}@adani.example'
            user.first_name = first
            user.last_name = last
            if created:
                user.set_password('password123')
            user.save()
            profile = user.employeeprofile
            profile.employee_id = f'ADN{index:04d}'
            profile.department = department
            profile.designation = designation
            profile.role = role
            profile.monthly_token_allowance = 100
            profile.save()
            profiles.append(profile)

        if not Recognition.objects.exists():
            Recognition.objects.create(
                sender=profiles[0],
                receiver=profiles[1],
                tokens=20,
                category=Recognition.Category.INNOVATION,
                message='Created a faster review flow that helped the team close pending items early.',
            )
            Recognition.objects.create(
                sender=profiles[2],
                receiver=profiles[4],
                tokens=30,
                category=Recognition.Category.SAFETY,
                message='Led a practical safety walkthrough and helped new teammates feel confident.',
            )
            Recognition.objects.create(
                sender=profiles[3],
                receiver=profiles[0],
                tokens=15,
                category=Recognition.Category.TEAMWORK,
                message='Jumped in during month-end and made cross-team coordination smooth.',
            )

        rewards = [
            (
                'Coffee voucher',
                'A quick appreciation treat for a strong contribution.',
                10,
                25,
            ),
            (
                'Learning stipend',
                'Support for a short course, workshop, or certification material.',
                40,
                10,
            ),
            (
                'Team lunch pass',
                'Redeem points toward a team lunch celebration.',
                60,
                8,
            ),
            (
                'Adani appreciation kit',
                'A branded recognition kit for standout employee impact.',
                80,
                5,
            ),
        ]
        for name, description, points_required, stock in rewards:
            RewardItem.objects.update_or_create(
                name=name,
                defaults={
                    'description': description,
                    'points_required': points_required,
                    'stock': stock,
                    'is_active': True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS('Demo ready. Login with nayan@adani.example / password123.')
        )
