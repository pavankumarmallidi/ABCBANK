from django.urls import path
from .views import register,regsuccess,login,lobby,logout,withdraw,withdrawsuccess,deposit,depositsuccess,transaction,transfer,transfer_success,forgotpassword,verify_otp,reset_password,resetsuccess
app_name='account'

urlpatterns = [
    path('register/',register,name='register'),
    path('login/',login,name='login'),
    path('success/',regsuccess,name='welcome_page'),
    path('lobby/',lobby,name='lobby'),
    path('logout/',logout,name='logout'),
    path('withdraw/',withdraw,name='withdraw'),
    path('deposit/',deposit,name='deposit'),
    path('withdraw/success/',withdrawsuccess),
    path('deposit/success/',depositsuccess),
    path('transaction/',transaction,name='transaction'),
    path('transfer/',transfer,name='transfer'),
    path('transfer/success/',transfer_success),
    path('forgotpassword/',forgotpassword,name='forgotpassword'),
    path('verify-otp/<str:username>/', verify_otp, name='verify_otp'),
    path('reset-password/<str:username>/', reset_password, name='reset_password'),
    path('reset/success/',resetsuccess,name='resetsuccess'),

]
