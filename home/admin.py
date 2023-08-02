from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import *


admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Permission)