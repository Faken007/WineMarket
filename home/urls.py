from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

from .forms import AuthenticationNewForm, PasswordChange

urlpatterns = [

    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
    path('homepage', views.homepage, name='homepage'),
    path('create_user/', views.UserCreateView.as_view(), name='create_user'),
    path("login/", auth_views.LoginView.as_view(form_class=AuthenticationNewForm), name="login"),
    path("password_change/", auth_views.PasswordChangeView.as_view(form_class=PasswordChange), name="password_change"),
    path('', include('django.contrib.auth.urls')),

]


