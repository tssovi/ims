from django import template
from ..models import NotificationSeen
register = template.Library()


@register.filter(name='add')
def add(a, b):
    return a+b


@register.filter(name='subtract')
def subtract(a, b):
    return a-b


@register.filter(name='percentage')
def percentage(a, b):
    p = a/b*100
    return p


@register.inclusion_tag('component/_notification.html')
def notifications(request):
    notification = NotificationSeen.objects.filter(
        user=request.user,
    ).select_related('notification').order_by('-id')
    count = len(notification.filter(has_seen=False))
    return {
        'notifications': notification[:10],
        'count': count
    }
