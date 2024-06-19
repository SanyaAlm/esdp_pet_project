from django.urls import path
from accounts import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user/update/<int:id>', views.UserUpdate.as_view(), name='update_user'),
    path('user/change-password/<int:id>', views.PasswordChangeView.as_view(), name='change_password'),
    path('sms-verification/', views.Sms_Verification.as_view(), name='sms-verification'),
    path('shop/<int:shop_id>/sign-in/', views.AccountLoginView.as_view(), name='account_login'),
    path('shop/<int:shop_id>/register/', views.AccountRegisterView.as_view(), name='account_register'),
    path('login-page/', views.LoginPageView.as_view(), name='login_page')
]
