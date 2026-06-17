from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.shortcuts import redirect, render

from .forms import RecognitionForm, RedemptionForm
from .models import EmployeeProfile, Recognition, Redemption, RewardItem


def can_access_admin_panel(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or user.employeeprofile.can_manage_rewards


@login_required
def dashboard(request):
    profile = request.user.employeeprofile
    profile.reset_monthly_budget_if_needed()

    if request.method == 'POST':
        form = RecognitionForm(request.POST, sender=profile)
        if form.is_valid():
            recognition = form.save(commit=False)
            recognition.sender = profile
            try:
                recognition.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    f'{recognition.tokens} tokens awarded to {recognition.receiver.display_name}.',
                )
                return redirect('dashboard')
    else:
        form = RecognitionForm(sender=profile)

    recognitions = Recognition.objects.select_related(
        'sender__user',
        'receiver__user',
    )[:12]
    leaderboard = (
        EmployeeProfile.objects.annotate(
            tokens_received=Sum('received_recognitions__tokens'),
            recognition_count=Count('received_recognitions'),
        )
        .order_by('-tokens_received', 'user__first_name')[:5]
    )
    totals = Recognition.objects.aggregate(
        tokens=Sum('tokens'),
        moments=Count('id'),
    )

    return render(
        request,
        'recognition/dashboard.html',
        {
            'form': form,
            'profile': profile,
            'recognitions': recognitions,
            'leaderboard': leaderboard,
            'total_tokens': totals['tokens'] or 0,
            'total_moments': totals['moments'] or 0,
            'employee_count': EmployeeProfile.objects.count(),
            'redeemable_points': profile.redeemable_points,
        },
    )


@login_required
def redeem_points(request):
    profile = request.user.employeeprofile

    if request.method == 'POST':
        form = RedemptionForm(request.POST, employee=profile)
        if form.is_valid():
            redemption = form.save(commit=False)
            redemption.employee = profile
            try:
                redemption.save()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    f'Redemption requested for {redemption.reward.name}.',
                )
                return redirect('redeem_points')
    else:
        form = RedemptionForm(employee=profile)

    return render(
        request,
        'recognition/redeem.html',
        {
            'form': form,
            'profile': profile,
            'rewards': RewardItem.objects.filter(is_active=True).order_by(
                'points_required',
                'name',
            ),
            'redemptions': Redemption.objects.select_related('reward').filter(
                employee=profile,
            )[:10],
        },
    )


@login_required
@user_passes_test(can_access_admin_panel)
def admin_panel(request):
    employees = (
        EmployeeProfile.objects.select_related('user')
        .annotate(
            tokens_received=Sum('received_recognitions__tokens'),
            recognitions_received=Count('received_recognitions'),
            recognitions_sent=Count('sent_recognitions'),
        )
        .order_by('department', 'user__first_name', 'user__last_name')
    )
    totals = EmployeeProfile.objects.aggregate(
        total_allowance=Sum('monthly_token_allowance'),
        total_sent=Sum('tokens_sent_this_month'),
    )
    redemptions = Redemption.objects.aggregate(total=Count('id'))

    return render(
        request,
        'recognition/admin_panel.html',
        {
            'employees': employees,
            'employee_count': employees.count(),
            'total_allowance': totals['total_allowance'] or 0,
            'total_sent': totals['total_sent'] or 0,
            'total_remaining': (totals['total_allowance'] or 0) - (totals['total_sent'] or 0),
            'redemption_count': redemptions['total'] or 0,
        },
    )
