from django.urls import path
from .views import (
    HouseListView, HouseDetailView, HouseCreateView, RegisterView, 
    CustomLoginView, CustomLogoutView, ProfileView, house_like_view, AboutView, ContactView
)

urlpatterns = [
    path('', HouseListView.as_view(), name='house-list'),
    path('<int:pk>/', HouseDetailView.as_view(), name='house-detail'),
    path('add/', HouseCreateView.as_view(), name='house-add'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('<int:pk>/like/', house_like_view, name='house-like'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
] 