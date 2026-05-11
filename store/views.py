from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.shortcuts import get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
import razorpay
from django.conf import settings
from django.contrib.auth.models import User
def create_admin(request):

    if not User.objects.filter(username='admin').exists():

        User.objects.create_superuser(
            'admin',
            'admin@gmail.com',
            'admin123'
        )

    return HttpResponse("admin created")

@login_required(login_url='/login/')
def home(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    else:
        products = Product.objects.all()

    category_id = request.GET.get('category')

    if category_id:
        products = products.filter(category_id=category_id)

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    categories = Category.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'cart_count': cart_count,
        'categories': categories
    })
    

@login_required(login_url='/login/')
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


@login_required(login_url='/login/')
def add_to_cart(request, id):
    cart = request.session.get('cart', {})

    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    request.session['cart'] = cart

    return redirect('cart')



@login_required(login_url='/login/')
def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for key, value in cart.items():
        product = Product.objects.get(id=key)
        product.quantity = value
        product.total_price = product.price * value
        total += product.total_price
        products.append(product)

    return render(request, 'cart.html', {'products': products, 'total': total})

@login_required(login_url='/login/')
def remove_from_cart(request, id):
    cart = request.session.get('cart', {})

    if str(id) in cart:
        del cart[str(id)]

    request.session['cart'] = cart
    return redirect('cart')

@login_required(login_url='/login/')
def update_cart(request,id, action):
    cart = request.session.get('cart',{})

    if str(id) in cart:
        if action == 'inc':
            cart[str(id)] += 1

        elif action == 'dec':
            cart[str(id)] -= 1

            if cart[str(id)] <= 0:
                del cart[str(id)]


    request.session['cart'] = cart
    return redirect('cart')

        




    

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']


        User.objects.create_user(username=username , password = password)
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password = password)

        if user:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html')



def user_logout(request):
    logout(request)
    return redirect('login')



def checkout(request):

    cart = request.session.get('cart', {})
    products = []
    total = 0

    for key, value in cart.items():

        product = Product.objects.get(id=key)

        product.quantity = value
        product.total_price = product.price * value

        total += product.total_price

        products.append(product)

    # Razorpay Client
    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    # Payment Order
    payment = client.order.create({
        'amount': total * 100,
        'currency': 'INR',
        'payment_capture': '1'
    })

    if request.method == 'POST':

        address = request.POST['address']
        payment_method = request.POST['payment']

        Order.objects.create(
            user=request.user,
            address=address,
            payment_method=payment_method,
            total_amount=total
        )

        html_content = render_to_string(
            'order_email.html',
            {
                'user': request.user,
                'address': address,
                'payment': payment_method,
                'total': total,
                'products': products
            }
        )

        email = EmailMultiAlternatives(
            'New Order Received',
            '',
            settings.EMAIL_HOST_USER,
            ['satyamray940@gmail.com']
        )

        email.attach_alternative(html_content, "text/html")

        email.send()

        request.session['cart'] = {}

        return redirect('success')

    return render(request, 'checkout.html', {
        'products': products,
        'total': total,
        'payment': payment,
        'settings': settings
    })

def order_success(request):
    return render(request,'success.html')



def add_to_wishlist(request, id):

    product = Product.objects.get(id=id)

    Wishlist.objects.create(
        user=request.user,
        product=product
    )

    return redirect('home')











