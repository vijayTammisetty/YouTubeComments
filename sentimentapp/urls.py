from django.urls import path
from sentimentapp import views

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('register/',views.user_register, name='register'),
    path('home/',views.home, name='user-home'),
    path('profile/',views.profile, name='profile'),

    # api url configurations 
    path('api-search/',views.api_search, name='api_search'),
    path('logout/',views.logout,name='logout'),
    
    
]
