from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def messages_page(request):
    """
    Main messages page - shows conversation list and chat interface.
    """
    return render(request, 'messaging/messages.html', {
        'page_title': 'Messages',
    })
