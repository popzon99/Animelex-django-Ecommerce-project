
from django.urls import path
from popapp import views

urlpatterns = [
   path('',views.home,name = 'home'),
   path('purchase',views.purchase,name='purchase'),
   path('checkout', views.checkout, name="checkout"),
   path('handlerequest/', views.handlerequest, name="HandleRequest"),
   path('tracker', views.tracker, name="TrackingStatus"),
   path('about', views.about, name="about"),
    path('payment', views.payment, name="payment"),
]