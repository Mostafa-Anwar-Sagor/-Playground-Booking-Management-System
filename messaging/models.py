from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
    """
    Represents a conversation between a user and a playground owner.
    """
    # Participants
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_conversations',
        help_text="The user (customer)"
    )
    playground_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner_conversations',
        help_text="The playground owner"
    )
    playground = models.ForeignKey(
        'playgrounds.Playground',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
        help_text="The playground this conversation is about"
    )
    
    # Metadata
    subject = models.CharField(max_length=255, blank=True, default="General Inquiry")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    archived_by_user = models.BooleanField(default=False)
    archived_by_owner = models.BooleanField(default=False)
    
    # Admin monitoring
    flagged_for_review = models.BooleanField(default=False, help_text="Admin flagged for review")
    admin_notes = models.TextField(blank=True, help_text="Admin can add notes here")
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['playground_owner', '-updated_at']),
            models.Index(fields=['flagged_for_review']),
        ]
        
    def __str__(self):
        playground_name = self.playground.name if self.playground else "No Playground"
        return f"{self.user.email} - {self.playground_owner.email} | {playground_name}"
    
    def get_other_participant(self, current_user):
        """Get the other participant in the conversation"""
        return self.playground_owner if current_user == self.user else self.user
    
    def unread_count_for_user(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(sender=self.get_other_participant(user), is_read=False).count()
    
    def last_message(self):
        """Get the last message in the conversation"""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """
    Represents a single message in a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messaging_sent_messages'
    )
    
    # Content
    content = models.TextField()
    attachment = models.FileField(
        upload_to='message_attachments/%Y/%m/%d/',
        blank=True,
        null=True
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # Admin monitoring
    flagged_inappropriate = models.BooleanField(default=False)
    admin_reviewed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['flagged_inappropriate']),
        ]
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}..."
    
    def mark_as_read(self):
        """Mark this message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def is_from_admin(self):
        """Check if message is from an admin"""
        return self.sender.is_staff or self.sender.is_superuser


class MessageReadReceipt(models.Model):
    """
    Track when messages are read by recipients (for group conversations in future).
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_receipts'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user')
        ordering = ['-read_at']
    
    def __str__(self):
        return f"{self.user.email} read message at {self.read_at}"
