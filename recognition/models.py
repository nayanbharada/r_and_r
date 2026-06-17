from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class EmployeeProfile(models.Model):
    class Role(models.TextChoices):
        EMPLOYEE = 'employee', 'Employee'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=80)
    designation = models.CharField(max_length=80)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    monthly_token_allowance = models.PositiveIntegerField(default=100)
    tokens_sent_this_month = models.PositiveIntegerField(default=0)
    last_reset_month = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        full_name = self.user.get_full_name()
        return full_name or self.user.username

    @property
    def tokens_remaining(self):
        return max(self.monthly_token_allowance - self.tokens_sent_this_month, 0)

    @property
    def points_received(self):
        total = self.received_recognitions.aggregate(total=models.Sum('tokens'))['total']
        return total or 0

    @property
    def points_redeemed(self):
        total = self.redemptions.aggregate(total=models.Sum('reward__points_required'))['total']
        return total or 0

    @property
    def redeemable_points(self):
        return max(self.points_received - self.points_redeemed, 0)

    @property
    def can_manage_rewards(self):
        return self.role in {self.Role.STAFF, self.Role.ADMIN}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        should_be_staff = self.can_manage_rewards
        should_be_superuser = self.role == self.Role.ADMIN
        if (
            self.user.is_staff != should_be_staff
            or self.user.is_superuser != should_be_superuser
        ):
            self.user.is_staff = should_be_staff
            self.user.is_superuser = should_be_superuser
            self.user.save(update_fields=['is_staff', 'is_superuser'])

    def reset_monthly_budget_if_needed(self):
        today = timezone.localdate()
        current_month = today.replace(day=1)
        saved_month = self.last_reset_month.replace(day=1)
        if saved_month != current_month:
            self.tokens_sent_this_month = 0
            self.last_reset_month = today
            self.save(update_fields=['tokens_sent_this_month', 'last_reset_month'])


class Recognition(models.Model):
    class Category(models.TextChoices):
        OWNERSHIP = 'ownership', 'Ownership'
        TEAMWORK = 'teamwork', 'Teamwork'
        INNOVATION = 'innovation', 'Innovation'
        CUSTOMER = 'customer', 'Customer Impact'
        SAFETY = 'safety', 'Safety'

    sender = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='sent_recognitions',
    )
    receiver = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='received_recognitions',
    )
    tokens = models.PositiveIntegerField()
    category = models.CharField(max_length=30, choices=Category.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender} awarded {self.tokens} tokens to {self.receiver}'

    def clean(self):
        if self.sender_id and self.receiver_id and self.sender_id == self.receiver_id:
            raise ValidationError('Employees cannot reward themselves.')
        if self.tokens <= 0:
            raise ValidationError('Tokens must be greater than zero.')
        if self.sender_id:
            self.sender.reset_monthly_budget_if_needed()
            if self.tokens > self.sender.tokens_remaining:
                raise ValidationError(
                    f'Only {self.sender.tokens_remaining} tokens are available this month.'
                )

    def save(self, *args, **kwargs):
        if self.pk:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            sender = EmployeeProfile.objects.select_for_update().get(pk=self.sender_id)
            sender.reset_monthly_budget_if_needed()
            if self.tokens > sender.tokens_remaining:
                raise ValidationError(
                    f'Only {sender.tokens_remaining} tokens are available this month.'
                )
            self.sender = sender
            self.full_clean()
            sender.tokens_sent_this_month += self.tokens
            sender.save(update_fields=['tokens_sent_this_month'])
            return super().save(*args, **kwargs)


class RewardItem(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    points_required = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['points_required', 'name']

    def __str__(self):
        return f'{self.name} ({self.points_required} points)'


class Redemption(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        APPROVED = 'approved', 'Approved'
        FULFILLED = 'fulfilled', 'Fulfilled'

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='redemptions',
    )
    reward = models.ForeignKey(
        RewardItem,
        on_delete=models.PROTECT,
        related_name='redemptions',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee} redeemed {self.reward}'

    def clean(self):
        if self.reward_id:
            if not self.reward.is_active:
                raise ValidationError('This reward is not active.')
            if self.reward.stock <= 0:
                raise ValidationError('This reward is out of stock.')
        if self.employee_id and self.reward_id:
            if self.reward.points_required > self.employee.redeemable_points:
                raise ValidationError(
                    f'You need {self.reward.points_required} points, but only have '
                    f'{self.employee.redeemable_points} available.'
                )

    def save(self, *args, **kwargs):
        if self.pk:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            reward = RewardItem.objects.select_for_update().get(pk=self.reward_id)
            employee = EmployeeProfile.objects.select_for_update().get(pk=self.employee_id)
            self.reward = reward
            self.employee = employee
            self.full_clean()
            reward.stock -= 1
            reward.save(update_fields=['stock'])
            return super().save(*args, **kwargs)
