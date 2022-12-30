from django.urls import path
from adminapp import views

urlpatterns = [
    path('login/',views.admin_login, name='admin_login'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('pending-users',views.pending_users, name='pending-users'),
    path('accept-user/<int:id>/',views.accept_user, name='accept-user'),
    path('reject-user/<int:id>/',views.reject_user, name='reject-user'),
    path('all-users/', views.all_users, name='all-users'),
    path('delete-user/<int:id>/',views.delete, name='delete_user'),
    path('logout/',views.logout,name='log-out'),
]
