from django import template

register = template.Library()

@register.filter
def has_pending_request(collection, user):
    return collection.access_requests.filter(requester=user, status='pending').exists()

@register.filter
def has_approved_request(collection, user):
    return collection.access_requests.filter(requester=user, status='approved').exists() 