from django.db import models

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('researching', 'Researching'),
        ('writing', 'Writing'),
        ('reviewing', 'Reviewing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    title = models.CharField(max_length=255, blank=True, null=True)
    source_text = models.TextField(help_text="The raw input text or extracted document text.")
    fact_sheet = models.JSONField(null=True, blank=True, help_text="Structured facts extracted by Agent 1.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Campaign {self.id}"

class ContentPiece(models.Model):
    CHANNEL_CHOICES = (
        ('blog', 'Blog Post'),
        ('social', 'Social Media Thread'),
        ('email', 'Email Teaser'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('rejected', 'Rejected by Editor'),
        ('approved', 'Approved by Editor'),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='pieces')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    content = models.TextField(help_text="The generated markdown content.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    editor_feedback = models.TextField(blank=True, null=True, help_text="Correction notes from Agent 3 or the User.")
    iteration_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_channel_display()} for {self.campaign}"

class AgentLog(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='logs')
    agent_name = models.CharField(max_length=50, help_text="e.g., 'Agent 1 (Research)', 'System'")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.agent_name}] {self.created_at}: {self.message[:50]}"
