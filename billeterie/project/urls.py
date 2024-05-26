from django.urls import path
from . import views

urlpatterns = [
    path('', views.destination_list, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('destination/', views.add_destination, name='add_destination'),
    path('payments/', views.payment_list, name='payment_list'),
    path('destination/<int:destination_id>/purchase/', views.purchase_ticket, name='purchase_ticket'),

]
