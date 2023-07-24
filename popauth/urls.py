
from django.urls import path
from popauth import views

urlpatterns = [
   path('signup/',views.signup,   name='signup'),
   path('login/',views.user_login,name = 'login'),
   path('logout/',views.user_logout,name = 'logout'),

   #class based view url
   path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
   #class based url for  requesting reset email
   path('request-reset-email/',views.RequestResetEmailView.as_view(),name='request-reset-email'),
   path('set-new-password/<uidb64>/<token>',views.SetNewPasswordView.as_view(),name='set-new-password'),
]