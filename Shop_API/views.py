from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product
from django.contrib.auth.mixins import LoginRequiredMixin

class Home(ListView):
    model = Product
    template_name = 'Shop_API/home.html'


class ProductDetails(DetailView):
    model = Product
    template_name = 'Shop_API/product_details.html'
