from django.urls import path
from mainapp import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/',views.about, name='about'),
    path('discography/', views.discography,name='discography'),
    path('contact/',views.contact,name='contact'),
]
