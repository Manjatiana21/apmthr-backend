from django import template

register = template.Library()

@register.filter
def non_lues_count(user):
    return user.notifications.filter(lu=False).count()
