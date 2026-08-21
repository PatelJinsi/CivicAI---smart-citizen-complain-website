
from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    CATEGORY_CHOICES = [
        ('road', 'Road & Infrastructure'),
        ('water', 'Water & Drainage'),
        ('garbage', 'Garbage & Sanitation'),
        ('electricity', 'Electricity & Street Lights'),
        ('other', 'Other'),
    ]

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('frustrated', 'Frustrated'),
    ]

    # Citizen info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')

    # Complaint details
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)

    # AI-predicted fields
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    category_confidence = models.FloatField(default=0.0)
    urgency_score = models.IntegerField(default=0)  # 0–100
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Status & timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-urgency_score', '-created_at']

    def __str__(self):
        return f"#{self.pk} — {self.title} ({dict(self.STATUS_CHOICES).get(self.status)})"

    def urgency_level(self):
        if self.urgency_score >= 75:
            return 'Critical'
        elif self.urgency_score >= 50:
            return 'High'
        elif self.urgency_score >= 25:
            return 'Medium'
        return 'Low'

    def urgency_color(self):
        if self.urgency_score >= 75:
            return 'danger'
        elif self.urgency_score >= 50:
            return 'warning'
        elif self.urgency_score >= 25:
            return 'info'
        return 'success'

    def status_color(self):
        colors = {
            'new': 'primary',
            'in_progress': 'warning',
            'resolved': 'success',
            'rejected': 'danger',
        }
        return colors.get(self.status, 'secondary')