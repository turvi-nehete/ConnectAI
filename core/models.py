from django.db import models
from django.contrib.auth.models import User 


#  ===========================
#  USER
#  ===========================

class Profile(models.Model):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("sales", "Sales"),
    ]

    AUTH_CHOICES = [
        ("local", "Local"),
        ("google", "Google"),
        ("linkedin", "LinkedIn"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="sales"
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AUTH_CHOICES,
        default="local"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# ===========================
# CLIENT
# ===========================

class Client(models.Model):

    CUSTOMER_CHOICES = [
        ("platinum", "Platinum"),
        ("gold", "Gold"),
        ("silver", "Silver"),
    ]

    COMPANY_CHOICES = [
        ("distributor", "Distributor"),
        ("hospital", "Hospital"),
        ("retail", "Retail"),
    ]

    cid = models.AutoField(primary_key=True)

    comp_name = models.CharField(max_length=200)

    contactname = models.CharField(max_length=100)

    c_mail = models.EmailField(unique=True)

    phone_no = models.CharField(max_length=15)

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    country = models.CharField(max_length=100)

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_CHOICES
    )

    comp_type = models.CharField(
        max_length=20,
        choices=COMPANY_CHOICES
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    uid = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="clients"
    )

    def __str__(self):
        return self.comp_name


# ===========================
# PRODUCT
# ===========================

class Product(models.Model):

    STATUS_CHOICES = [
        ("available", "Available"),
        ("delayed", "Delayed"),
        ("recalled", "Recalled"),
    ]

    pid = models.AutoField(primary_key=True)

    batch_no = models.CharField(max_length=100)

    product_name = models.CharField(max_length=200)

    category = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
    )

    def __str__(self):
        return self.product_name

from django.db import models


# ===========================
# CAMPAIGN
# ===========================

class Campaign(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("sent", "Sent"),
    ]

    cam_id = models.AutoField(primary_key=True)

    cap_name = models.CharField(max_length=200)

    prompt = models.TextField()

    subj = models.CharField(max_length=255)

    mail_body = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    template = models.ForeignKey(
    "Template",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="campaigns"
    )

    parent_campaign = models.ForeignKey(
    "self",
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="reminders",
    )

    is_reminder = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cap_name


# ===========================
# CAMPAIGN RECIPIENT
# ===========================

class CampaignRecipient(models.Model):

    rid = models.AutoField(primary_key=True)

    cam_id = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="recipients"
    )

    cid = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )

    del_status = models.CharField(
        max_length=50,
        default="Pending"
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    replied = models.BooleanField(default=False)

    replied_message = models.TextField(blank=True, default="")

    replied_at = models.DateTimeField(
      null=True,
      blank=True
    )

    thread_id = models.CharField(
      max_length=255,
      blank=True,
      default=""
    )

    message_id = models.CharField(
      max_length=255,
      blank=True,
      default=""
    )

    def __str__(self):
        return f"{self.cam_id.cap_name} -> {self.cid.comp_name}"


# ===========================
# MEETING
# ===========================

class Meeting(models.Model):

    mid = models.AutoField(primary_key=True)

    title = models.CharField(max_length=200)

    agenda = models.TextField()

    meeting_date = models.DateField()

    meeting_time = models.TimeField()

    duration_minutes = models.PositiveIntegerField(
        default=30
    )

    uid = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="meetings"
    )

    google_event_id = models.CharField(
        max_length=255,
        unique=True
    )

    google_meet_link = models.URLField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title
    
from django.db import models


# ===========================
# MEETING PARTICIPANT
# ===========================

class MeetingParticipant(models.Model):

    STATUS_CHOICES = [
        ("accepted", "Accepted"),
        ("pending", "Pending"),
        ("declined", "Declined"),
    ]

    mp_id = models.AutoField(primary_key=True)

    mid = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    cid = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="meetings"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    def __str__(self):
        return f"{self.cid.comp_name} - {self.mid.title}"


# ===========================
# AUDIT LOG
# ===========================

class AuditLog(models.Model):

    aid = models.AutoField(primary_key=True)

    uid = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )

    action = models.CharField(max_length=100)

    prompt = models.TextField()

    tool_used = models.CharField(max_length=100)

    timestamp = models.DateTimeField(auto_now_add=True)

    success = models.BooleanField(default=True)

    def __str__(self):
     return f"{self.action} ({self.uid.username})"


# ===========================
# AI PROMPT HISTORY
# ===========================

class AIPromptHistory(models.Model):

    hid = models.AutoField(primary_key=True)

    uid = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="prompt_history"
    )

    prompt = models.TextField()

    generated_output = models.TextField()

    llm_used = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
     return f"Prompt {self.hid} - {self.uid.username}"
    
from django.db import models


# ===========================
# TEMPLATE
# ===========================

class Template(models.Model):

    CATEGORY_CHOICES = [
        ("reminder", "Reminder"),
        ("discount", "Discount"),
        ("shipment_delay", "Shipment Delay"),
    ]

    tid = models.AutoField(primary_key=True)

    temp_name = models.CharField(max_length=200)

    subj = models.CharField(max_length=255)

    body = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    ) 

    def __str__(self):
        return self.temp_name