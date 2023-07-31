from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from .models import *
from home.models import Product
from django.http import JsonResponse
import json


class CreateProductView(CreateView):
    template_name = 'create_product.html'
    model = Product
    fields = '__all__'


def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items =[]
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store.html', context )


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items =[]
        order ={'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart.html', context )


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items =[]
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'checkout.html', context)




def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated.'}, status=400)

    customer = request.user.customer
    try:
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = orderItem.quantity + 1
        elif action == 'remove':
            orderItem.quantity = orderItem.quantity - 1

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        return JsonResponse({'message': 'Item was updated successfully.'}, status=200)

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product does not exist.'}, status=400)

    except Exception as e:
        return JsonResponse({'error': 'An error occurred while updating the item.'}, status=500)
