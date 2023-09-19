from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('register/', views.register, name="register"),
    path('login/', views.kullanici_giris, name="login"),
    path('logout/', views.cikis, name="cikis"),
    path('forgotpassword/', views.forgotpassword, name="forgotpassword"),
    path('nesne_tanima/', views.nesne_tanıma, name='nesne_tanıma'),

]
