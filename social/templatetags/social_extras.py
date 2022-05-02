from django import template
from django.urls import reverse
from django.utils.html import escape

def display_message(message, username):
    url = reverse('social:messages')
    time = str(message.time)[:16] + ' '
    sender = '<a href="' + str(url) + '?view=' + message.sender.username + '">' + message.sender.username + '</a> '
    if message.public:
        text = 'wrote: ' + escape(message.text) + ' '
    else:
        text = 'whispered: <span class="whisper">' + escape(message.text) + '</span>' + ' '
    if message.sender.username==username or message.recip.username==username:
        button = '<button type="button" class="btn btn-sm btn-danger border remove-btn ml-2"><i class="far fa-trash-alt"></i></button>'
    else:
        button = ''
    return '<div id="' + str(message.id) + '">' + time + sender + text + button + '</div>'

register = template.Library()
register.filter('display_message', display_message)
