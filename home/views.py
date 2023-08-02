from django.core.mail import EmailMessage
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from WineMarket.settings import EMAIL_HOST_USER
from .forms import UserForm
from .models import *
from home.models import Product
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder



def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart.html', context )


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
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


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created =Order.objects.get_or_create(customer=customer, complete=False)


    else:
        customer, order = guestOrder(request, data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('payment complete!', safe=False)

class UserCreateView(CreateView):
    template_name = 'create_user.html'
    model = User
    form_class = UserForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        if form.is_valid():
            new_user = form.save(commit=False)  # aici salvam datele in tabele auth_user
            new_user.first_name = new_user.first_name.title()
            # -> atribui valoare new_user.first_name.title() campului first_name al obiectului new_user
            new_user.last_name = new_user.last_name.title()
            new_user.username = f'{new_user.first_name[0].lower()}{new_user.last_name.lower().replace(" ", "")}'

            new_user.save()

            # Trimiterea de mail FARA template
            # subject = 'Confirmare cont nou!'
            # message = f'Salut, {new_user.first_name} {new_user.last_name}. Numele tau de utilzator este: {new_user.username}'
            # send_mail(subject, message, EMAIL_HOST_USER, [new_user.email])

            # Add history
            history_text = f'Userul a fost adaugat la data de {datetime.datetime.now()}. Firstname {new_user.first_name},' \
                           f'Last name: {new_user.last_name}, Email: {new_user.email}, Username:{new_user.username}.'

            History.objects.create(text=history_text, created_at=datetime.datetime.now())

            # # Trimiterea de mail CU TEMPLATE
            # details_user = {
            #     'fullname': f'{new_user.first_name} {new_user.last_name}',
            #     'username': new_user.username,
            # }
            # subject = 'Confirmare cont nou in aplicatie'
            # message = get_template('mail.html').render(details_user)
            #
            # mail = EmailMessage(subject, message, EMAIL_HOST_USER, [new_user.email])
            # mail.content_subtype = 'html'
            # mail.send()

        return super().form_valid(form)

