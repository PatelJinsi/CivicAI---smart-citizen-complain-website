

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Complaint, Department
from .forms import RegisterForm, ComplaintForm, StatusUpdateForm
from .ai_engine import analyze_complaint


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def is_admin(user):
    return user.is_authenticated and user.is_staff


# ─── PUBLIC VIEWS ─────────────────────────────────────────────────────────────

def home(request):
    stats = {
        'total': Complaint.objects.count(),
        'resolved': Complaint.objects.filter(status='resolved').count(),
        'in_progress': Complaint.objects.filter(status='in_progress').count(),
    }
    return render(request, 'home.html', {'stats': stats})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Account created successfully.')
            return redirect('submit_complaint')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_staff else 'my_complaints')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard' if user.is_staff else 'my_complaints')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── CITIZEN VIEWS ────────────────────────────────────────────────────────────

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user

            # ── RUN AI ENGINE ──
            ai_result = analyze_complaint(complaint.title, complaint.description)
            complaint.category = ai_result['category']
            complaint.category_confidence = ai_result['category_confidence']
            complaint.urgency_score = ai_result['urgency_score']
            complaint.sentiment = ai_result['sentiment']

            # Auto-assign department
            dept, _ = Department.objects.get_or_create(
                name=ai_result['department_name'],
                defaults={'description': f'Handles {ai_result["category"]} related complaints'},
            )
            complaint.department = dept

            complaint.save()
            messages.success(request, '✅ Complaint submitted! AI has analyzed and categorized it.')
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm()
    return render(request, 'complaints/submit.html', {'form': form})


@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)

    # Filters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)

    context = {
        'complaints': complaints,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': Complaint.STATUS_CHOICES,
        'category_choices': Complaint.CATEGORY_CHOICES,
        'counts': {
            'total': Complaint.objects.filter(user=request.user).count(),
            'resolved': Complaint.objects.filter(user=request.user, status='resolved').count(),
            'in_progress': Complaint.objects.filter(user=request.user, status='in_progress').count(),
            'new': Complaint.objects.filter(user=request.user, status='new').count(),
        }
    }
    return render(request, 'complaints/my_complaints.html', context)


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    # Citizens can only see their own complaints
    if not request.user.is_staff and complaint.user != request.user:
        messages.error(request, 'You do not have permission to view this complaint.')
        return redirect('my_complaints')

    status_form = None
    if request.user.is_staff:
        if request.method == 'POST':
            status_form = StatusUpdateForm(request.POST, instance=complaint)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, '✅ Complaint status updated.')
                return redirect('complaint_detail', pk=pk)
        else:
            status_form = StatusUpdateForm(instance=complaint)

    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'status_form': status_form,
    })


# ─── ADMIN DASHBOARD ──────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    complaints = Complaint.objects.select_related('user', 'department').all()

    # Filters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    urgency_filter = request.GET.get('urgency', '')

    if search:
        complaints = complaints.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search) |
            Q(user__username__icontains=search)
        )
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if urgency_filter == 'high':
        complaints = complaints.filter(urgency_score__gte=75)
    elif urgency_filter == 'medium':
        complaints = complaints.filter(urgency_score__gte=50, urgency_score__lt=75)
    elif urgency_filter == 'low':
        complaints = complaints.filter(urgency_score__lt=50)

    # Stats
    all_complaints = Complaint.objects.all()
    stats = {
        'total': all_complaints.count(),
        'new': all_complaints.filter(status='new').count(),
        'in_progress': all_complaints.filter(status='in_progress').count(),
        'resolved': all_complaints.filter(status='resolved').count(),
        'urgent': all_complaints.filter(urgency_score__gte=75).count(),
        'avg_urgency': all_complaints.aggregate(avg=Avg('urgency_score'))['avg'] or 0,
    }

    # Chart data
    category_data = all_complaints.values('category').annotate(count=Count('id'))
    chart_labels = [item['category'].title() for item in category_data]
    chart_values = [item['count'] for item in category_data]

    context = {
        'complaints': complaints,
        'stats': stats,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'search': search,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'urgency_filter': urgency_filter,
        'status_choices': Complaint.STATUS_CHOICES,
        'category_choices': Complaint.CATEGORY_CHOICES,
    }
    return render(request, 'complaints/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def quick_status_update(request, pk):
    """AJAX endpoint for quick status update from dashboard table."""
    complaint = get_object_or_404(Complaint, pk=pk)
    new_status = request.POST.get('status')
    valid_statuses = [s[0] for s in Complaint.STATUS_CHOICES]
    if new_status in valid_statuses:
        complaint.status = new_status
        complaint.save()
        return JsonResponse({'success': True, 'status': dict(Complaint.STATUS_CHOICES).get(complaint.status)})
    return JsonResponse({'success': False}, status=400)


# ─── API: RE-ANALYZE ──────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def reanalyze_complaint(request, pk):
    """Re-run AI analysis on an existing complaint."""
    complaint = get_object_or_404(Complaint, pk=pk)
    ai_result = analyze_complaint(complaint.title, complaint.description)
    complaint.category = ai_result['category']
    complaint.category_confidence = ai_result['category_confidence']
    complaint.urgency_score = ai_result['urgency_score']
    complaint.sentiment = ai_result['sentiment']
    dept, _ = Department.objects.get_or_create(name=ai_result['department_name'])
    complaint.department = dept
    complaint.save()
    messages.success(request, '🤖 AI re-analysis complete.')
    return redirect('complaint_detail', pk=pk)