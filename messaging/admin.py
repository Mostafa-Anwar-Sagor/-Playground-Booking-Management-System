from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Conversation, Message, MessageReadReceipt


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'owner_link', 'playground_link', 'message_count', 
                    'last_message_preview', 'flagged_badge', 'is_active', 'updated_at']
    list_filter = ['is_active', 'flagged_for_review', 'created_at', 'updated_at']
    search_fields = ['user__email', 'playground_owner__email', 'playground__name', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'conversation_preview']
    
    fieldsets = (
        ('Participants', {
            'fields': ('user', 'playground_owner', 'playground')
        }),
        ('Details', {
            'fields': ('subject', 'is_active', 'archived_by_user', 'archived_by_owner')
        }),
        ('Admin Monitoring', {
            'fields': ('flagged_for_review', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Preview', {
            'fields': ('conversation_preview',),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'
    
    def owner_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.playground_owner.id])
        return format_html('<a href="{}">{}</a>', url, obj.playground_owner.email)
    owner_link.short_description = 'Playground Owner'
    
    def playground_link(self, obj):
        if obj.playground:
            url = reverse('admin:playgrounds_playground_change', args=[obj.playground.id])
            return format_html('<a href="{}">{}</a>', url, obj.playground.name)
        return '-'
    playground_link.short_description = 'Playground'
    
    def message_count(self, obj):
        count = obj.messages.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    message_count.short_description = 'Messages'
    
    def last_message_preview(self, obj):
        last_msg = obj.last_message()
        if last_msg:
            preview = last_msg.content[:50] + '...' if len(last_msg.content) > 50 else last_msg.content
            return format_html(
                '<span style="color: #666;" title="{}">{}</span>',
                last_msg.content,
                preview
            )
        return '-'
    last_message_preview.short_description = 'Last Message'
    
    def flagged_badge(self, obj):
        if obj.flagged_for_review:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">🚩 FLAGGED</span>'
            )
        return format_html('<span style="color: #28a745;">✓ OK</span>')
    flagged_badge.short_description = 'Status'
    
    def conversation_preview(self, obj):
        """Show all messages in this conversation"""
        messages = obj.messages.all()[:20]  # Last 20 messages
        
        if not messages:
            return "No messages yet"
        
        html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; max-height: 500px; overflow-y: auto;">'
        html += f'<h3 style="margin-top: 0;">Conversation Messages ({obj.messages.count()} total)</h3>'
        
        for msg in messages:
            sender_badge = "🛡️ ADMIN" if msg.sender.is_staff else ("👤 User" if msg.sender == obj.user else "🏢 Owner")
            read_badge = "✓ Read" if msg.is_read else "● Unread"
            flag_badge = "🚩 FLAGGED" if msg.flagged_inappropriate else ""
            
            bg_color = "#e3f2fd" if msg.sender == obj.user else "#fff3cd"
            
            html += f'''
            <div style="background: {bg_color}; padding: 10px; margin-bottom: 10px; border-radius: 6px; border-left: 3px solid #007bff;">
                <div style="font-size: 11px; color: #666; margin-bottom: 5px;">
                    <strong>{msg.sender.email}</strong> 
                    <span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; margin-left: 5px;">{sender_badge}</span>
                    <span style="background: {'#28a745' if msg.is_read else '#dc3545'}; color: white; padding: 2px 6px; border-radius: 3px; margin-left: 5px;">{read_badge}</span>
                    {f'<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; margin-left: 5px;">{flag_badge}</span>' if flag_badge else ''}
                    <span style="float: right;">{msg.created_at.strftime("%Y-%m-%d %H:%M")}</span>
                </div>
                <div style="font-size: 13px;">{msg.content}</div>
                {f'<div style="margin-top: 5px;"><a href="{msg.attachment.url}" target="_blank">📎 Attachment</a></div>' if msg.attachment else ''}
            </div>
            '''
        
        html += '</div>'
        return mark_safe(html)
    conversation_preview.short_description = 'Full Conversation'
    
    actions = ['flag_for_review', 'unflag', 'archive_conversation']
    
    def flag_for_review(self, request, queryset):
        updated = queryset.update(flagged_for_review=True)
        self.message_user(request, f'{updated} conversation(s) flagged for review.')
    flag_for_review.short_description = '🚩 Flag selected conversations for review'
    
    def unflag(self, request, queryset):
        updated = queryset.update(flagged_for_review=False)
        self.message_user(request, f'{updated} conversation(s) unflagged.')
    unflag.short_description = '✓ Remove flag from selected conversations'
    
    def archive_conversation(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} conversation(s) archived.')
    archive_conversation.short_description = '📦 Archive selected conversations'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation_link', 'sender_link', 'content_preview', 
                    'is_read', 'flagged_badge', 'created_at']
    list_filter = ['is_read', 'flagged_inappropriate', 'admin_reviewed', 'created_at']
    search_fields = ['sender__email', 'content', 'conversation__subject']
    readonly_fields = ['created_at', 'edited_at', 'read_at']
    
    fieldsets = (
        ('Message Info', {
            'fields': ('conversation', 'sender', 'content', 'attachment')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_deleted')
        }),
        ('Admin Monitoring', {
            'fields': ('flagged_inappropriate', 'admin_reviewed'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'edited_at'),
            'classes': ('collapse',)
        })
    )
    
    def conversation_link(self, obj):
        url = reverse('admin:messaging_conversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">Conversation #{}</a>', url, obj.conversation.id)
    conversation_link.short_description = 'Conversation'
    
    def sender_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.sender.id])
        badge = "🛡️" if obj.sender.is_staff else "👤"
        return format_html('{} <a href="{}">{}</a>', badge, url, obj.sender.email)
    sender_link.short_description = 'Sender'
    
    def content_preview(self, obj):
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, preview)
    content_preview.short_description = 'Content'
    
    def flagged_badge(self, obj):
        if obj.flagged_inappropriate:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">🚩 FLAGGED</span>'
            )
        return format_html('<span style="color: #28a745;">✓ OK</span>')
    flagged_badge.short_description = 'Status'
    
    actions = ['flag_as_inappropriate', 'mark_as_reviewed', 'mark_as_read']
    
    def flag_as_inappropriate(self, request, queryset):
        updated = queryset.update(flagged_inappropriate=True)
        self.message_user(request, f'{updated} message(s) flagged as inappropriate.')
    flag_as_inappropriate.short_description = '🚩 Flag as inappropriate'
    
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(admin_reviewed=True, flagged_inappropriate=False)
        self.message_user(request, f'{updated} message(s) marked as reviewed.')
    mark_as_reviewed.short_description = '✓ Mark as reviewed'
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = '✓ Mark as read'


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'message_link', 'user_link', 'read_at']
    list_filter = ['read_at']
    search_fields = ['user__email', 'message__content']
    readonly_fields = ['read_at']
    
    def message_link(self, obj):
        url = reverse('admin:messaging_message_change', args=[obj.message.id])
        return format_html('<a href="{}">Message #{}</a>', url, obj.message.id)
    message_link.short_description = 'Message'
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'
