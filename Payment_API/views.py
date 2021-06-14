from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
from .models import BillingAddress
from .forms import BillingForm
from Order_API.models import Cart, Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import requests
import socket

from django.views.decorators.csrf import csrf_exempt


@login_required
def check_out(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method == 'POST':
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.success(request, "Your shipping address has been successfully saved")

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    orderitems = order_qs[0].order_items.all()
    order_total = order_qs[0].get_totals()


    return render(request, 'Payment_API/check_out.html', context={'form':form, 'orderitems':orderitems, 'order_total':order_total, 'saved_address':saved_address})


@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    if not saved_address.is_fully_filled():
        messages.info(request, "Shipping adderss is not complete")
        return redirect('Payment_API:check_out')

    if not request.user.profile.is_full_field():
        messages.info(request, "User info is not complete")
        return redirect('Login_API:profile')

    store_id = 'easyl5ef49b890c659'
    API_Key = 'easyl5ef49b890c659@ssl'

    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id, sslc_store_pass=API_Key)

    status_url = request.build_absolute_uri(reverse('Payment_API:complete'))

    mypayment.set_urls(success_url=status_url, fail_url=status_url, cancel_url=status_url, ipn_url=status_url)

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    orderitems = order_qs[0].order_items.all()
    order_item_count = order_qs[0].order_items.count()
    order_total = order_qs[0].get_totals()

    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='BDT', product_category='Mixed', product_name=orderitems, num_of_item=order_item_count, shipping_method='Courier', product_profile='None')

    current_user = request.user

    mypayment.set_customer_info(name=current_user.profile.full_name, email=current_user.email, address1=current_user.profile.adderss_1, address2=current_user.profile.adderss_1, city=current_user.profile.city, postcode=current_user.profile.zipcode, country=current_user.profile.country, phone=current_user.profile.phone)

    mypayment.set_shipping_info(shipping_to=current_user.profile.full_name, address=saved_address.address, city=saved_address.city, postcode=saved_address.zip_code, country=saved_address.country)

    response_data = mypayment.init_payment()

    return redirect(response_data['GatewayPageURL'])

@csrf_exempt
def complete(request):
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']
        print(status)
        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, "Your payment has been completed successfully")
            return HttpResponseRedirect(reverse('Payment_API:purchase', kwargs={'val_id':val_id, 'tran_id':tran_id}))
        elif status == 'FAILED':
            messages.warning(request, "Your payment has failed!")

    return render(request, 'Payment_API/complete.html', context={})


@login_required
def purchase(request, val_id, tran_id):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    order.ordered = True
    order.order_id = tran_id
    order.payment_id = val_id
    order.save()

    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    for item in cart_items:
        item.purchased = True
        item.save()

    return HttpResponseRedirect(reverse('Shop_API:home'))

@login_required
def order_view(request):
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {'orders':orders}
    except:
        messages.warning(request, "There is no active order")
        return redirect('Shop_API:home')
    return render(request, 'Payment_API/order.html', context)
