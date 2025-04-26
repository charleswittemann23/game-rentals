from django import template
from catalog.models import BorrowRequest, Loan

register = template.Library()

@register.filter
def is_borrowed_by(game, user):
    return game.is_on_loan and game.current_borrower == user

@register.filter
def has_pending_borrow_request(game):
    return BorrowRequest.objects.filter(game=game, status='pending').exists()
