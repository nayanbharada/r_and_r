from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EmployeeProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_employee_profile(sender, instance, created, **kwargs):
    if not created or hasattr(instance, 'employeeprofile'):
        return

    role = EmployeeProfile.Role.EMPLOYEE
    if instance.is_superuser:
        role = EmployeeProfile.Role.ADMIN
    elif instance.is_staff:
        role = EmployeeProfile.Role.STAFF

    EmployeeProfile.objects.create(
        user=instance,
        employee_id=f'ADN{instance.pk:04d}',
        department='Corporate',
        designation='Employee',
        role=role,
    )
