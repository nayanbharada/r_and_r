from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import EmployeeProfile, Recognition, Redemption, RewardItem


class RecognitionRulesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.sender = User.objects.create_user(
            username='sender',
            password='password123',
            first_name='Sender',
        ).employeeprofile
        self.receiver = User.objects.create_user(
            username='receiver',
            password='password123',
            first_name='Receiver',
        ).employeeprofile
        self.sender.monthly_token_allowance = 25
        self.sender.save()

    def test_reward_consumes_sender_monthly_tokens(self):
        Recognition.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            tokens=10,
            category=Recognition.Category.TEAMWORK,
            message='Great collaboration.',
        )

        self.sender.refresh_from_db()
        self.assertEqual(self.sender.tokens_sent_this_month, 10)
        self.assertEqual(self.sender.tokens_remaining, 15)

    def test_reward_cannot_exceed_remaining_tokens(self):
        with self.assertRaises(ValidationError):
            Recognition.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                tokens=30,
                category=Recognition.Category.OWNERSHIP,
                message='Excellent ownership.',
            )

    def test_employee_cannot_reward_self(self):
        with self.assertRaises(ValidationError):
            Recognition.objects.create(
                sender=self.sender,
                receiver=self.sender,
                tokens=5,
                category=Recognition.Category.INNOVATION,
                message='Self reward should fail.',
            )


class EmailLoginTests(TestCase):
    def test_user_can_login_with_email_and_password(self):
        User = get_user_model()
        User.objects.create_user(
            username='nayan',
            email='nayan@adani.example',
            password='password123',
        )

        response = self.client.post(
            reverse('login'),
            {'username': 'nayan@adani.example', 'password': 'password123'},
        )

        self.assertRedirects(response, reverse('dashboard'))


class AdminPanelTests(TestCase):
    def test_staff_user_can_view_employee_panel(self):
        User = get_user_model()
        staff = User.objects.create_user(
            username='admin',
            email='admin@adani.example',
            password='password123',
            first_name='Admin',
            is_staff=True,
        )
        User.objects.create_user(
            username='employee',
            email='employee@adani.example',
            password='password123',
            first_name='Employee',
        )

        self.client.force_login(staff)
        response = self.client.get(reverse('admin_panel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All employees')
        self.assertContains(response, 'employee@adani.example')

    def test_non_staff_user_cannot_view_employee_panel(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='employee',
            email='employee@adani.example',
            password='password123',
        )

        self.client.force_login(user)
        response = self.client.get(reverse('admin_panel'))

        self.assertEqual(response.status_code, 302)

    def test_profile_role_syncs_django_staff_flags(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='manager',
            email='manager@adani.example',
            password='password123',
        )

        user.employeeprofile.role = EmployeeProfile.Role.STAFF
        user.employeeprofile.save()
        user.refresh_from_db()

        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

        user.employeeprofile.role = EmployeeProfile.Role.ADMIN
        user.employeeprofile.save()
        user.refresh_from_db()

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_staff_employee_can_send_and_receive_rewards(self):
        User = get_user_model()
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@adani.example',
            password='password123',
        )
        employee_user = User.objects.create_user(
            username='employee2',
            email='employee2@adani.example',
            password='password123',
        )
        staff_profile = staff_user.employeeprofile
        staff_profile.role = EmployeeProfile.Role.STAFF
        staff_profile.monthly_token_allowance = 50
        staff_profile.save()
        employee_profile = employee_user.employeeprofile

        Recognition.objects.create(
            sender=staff_profile,
            receiver=employee_profile,
            tokens=10,
            category=Recognition.Category.TEAMWORK,
            message='Helpful team support.',
        )
        Recognition.objects.create(
            sender=employee_profile,
            receiver=staff_profile,
            tokens=5,
            category=Recognition.Category.OWNERSHIP,
            message='Clear direction and ownership.',
        )

        staff_profile.refresh_from_db()
        self.assertEqual(staff_profile.tokens_sent_this_month, 10)
        self.assertEqual(staff_profile.received_recognitions.count(), 1)


class RedemptionRulesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.sender = User.objects.create_user(
            username='sender2',
            email='sender2@adani.example',
            password='password123',
        ).employeeprofile
        self.employee = User.objects.create_user(
            username='redeemer',
            email='redeemer@adani.example',
            password='password123',
        ).employeeprofile
        self.reward = RewardItem.objects.create(
            name='Coffee voucher',
            description='A quick appreciation treat.',
            points_required=10,
            stock=2,
        )

    def test_employee_can_redeem_received_points(self):
        Recognition.objects.create(
            sender=self.sender,
            receiver=self.employee,
            tokens=15,
            category=Recognition.Category.TEAMWORK,
            message='Great work.',
        )

        Redemption.objects.create(employee=self.employee, reward=self.reward)

        self.reward.refresh_from_db()
        self.assertEqual(self.reward.stock, 1)
        self.assertEqual(self.employee.redeemable_points, 5)

    def test_employee_cannot_redeem_more_than_available_points(self):
        Recognition.objects.create(
            sender=self.sender,
            receiver=self.employee,
            tokens=5,
            category=Recognition.Category.TEAMWORK,
            message='Great work.',
        )

        with self.assertRaises(ValidationError):
            Redemption.objects.create(employee=self.employee, reward=self.reward)

    def test_employee_cannot_redeem_out_of_stock_reward(self):
        self.reward.stock = 0
        self.reward.save()
        Recognition.objects.create(
            sender=self.sender,
            receiver=self.employee,
            tokens=15,
            category=Recognition.Category.TEAMWORK,
            message='Great work.',
        )

        with self.assertRaises(ValidationError):
            Redemption.objects.create(employee=self.employee, reward=self.reward)
