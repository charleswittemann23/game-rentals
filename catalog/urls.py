from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path("", views.index, name="index"),
    path('add/', views.add_game, name='add_game'),
    path('edit/<str:upc>/', views.edit_game, name='edit_game'),
    path('request-borrow/<str:upc>/', views.request_borrow, name='request_borrow'),
    path('my-loans/', views.my_loans, name='my_loans'),
    path('manage-borrow-requests/', views.manage_borrow_requests, name='manage_borrow_requests'),
    path('approve-borrow-request/<int:request_id>/', views.approve_borrow_request, name='approve_borrow_request'),
    path('reject-borrow-request/<int:request_id>/', views.reject_borrow_request, name='reject_borrow_request'),
    path('delete/<str:upc>/', views.delete_game, name='delete_game'),
    path('game/<str:upc>/', views.game_detail, name='game_detail'),
    path('game/<str:upc>/return/', views.return_game, name='return_game'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]
