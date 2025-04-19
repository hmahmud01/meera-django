import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from .models import *



def cookieCart(request):

    # Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        print('CART:', cart)

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'id': product.id,
                'product': {'id': product.id, 'name': product.name, 'price': product.price,
                            'imageURL': product.imageURL}, 'quantity': cart[i]['quantity'],
                'digital': product.digital, 'get_total': total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.username
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitems_set.all()
        cartItems = order.get_cart_items
    else:
        customer = "guest"
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitems_set.all()
        cartItems = order.get_cart_items

    return {'cartItems': cartItems, 'order': order, 'items': items}

def send_order_email(order, customer_email):
    print(f"ORDER : {order.trx_id}")
    print(f"EMAIL: {customer_email}")
    subject = f"Order Confirmation - #{order.trx_id}"
    charge = ShippingCharge.objects.get(type="local")
    total = order.get_cart_total + charge.charge
    # Load email content from a template
    context = {
        "order": order,
        "customer_email": customer_email,
        "total": total
    }
    message = render_to_string("emails/order_confirmation.html", context)

    # Send email to both store owner and customer
    recipients = ["retail.meeraseed@gmail.com", customer_email]

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
    email.content_subtype = "html"  # Ensure HTML rendering
    email.send()
