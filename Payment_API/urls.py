from django.urls import path
from Payment_API import views

app_name = 'Payment_API'

urlpatterns = [
    path('check_out/', views.check_out, name='check_out'),
    path('payment/', views.payment, name='payment'),
    path('complete/', views.complete, name='complete'),
    path('purchased/<val_id>/<tran_id>/', views.purchase, name='purchase'),
    path('order/', views.order_view, name='order'),
]
