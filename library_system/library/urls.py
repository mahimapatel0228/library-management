from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('members/', views.member_list, name='member_list'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('issue/<int:book_id>/<int:member_id>/', views.issue_book, name='issue_book'),
    path('return/<int:txn_id>/', views.return_book, name='return_book'),
    path('import/', views.import_books, name='import_books'),
    path('add-member/', views.add_member, name='add_member')
]
