from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from .models import Store, Product, Purchase, Review, ResetToken
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.conf import settings
import secrets
from hashlib import sha1
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseForbidden
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    StoreSerializer,
    ProductSerializer,
    ReviewSerializer,
)
from .functions.reddit import get_reddit_posts


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        role = request.POST.get('role')

        if password != confirm_password:
            return render(
                request,
                "get_your_goods/register.html",
                {"error": "Passwords do not match."}
            )
        
        try:
            validate_password(password)
        except ValidationError as e:
            return render(
                request,
                "get_your_goods/register.html",
                {"error": " ".join(e.messages)}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "get_your_goods/register.html",
                {"error": "That username is already taken."}
            )
        if User.objects.filter(email=email).exists():
            return render(
                request,
                "get_your_goods/register.html",
                {
                    "error": "An account with this email address "
                    "already exists."
                    }
                    )

        user = User.objects.create_user(username=username,
                                        password=password, email=email)
        try:
            if role == "vendor":
                group = Group.objects.get(name="Vendors")
            else:
                group = Group.objects.get(name="Buyers")

            user.groups.add(group)
        except Group.DoesNotExist:
            pass

        login(request, user)
        return redirect('get_your_goods:welcome')
    return render(request, 'get_your_goods/register.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username,
                            password=password)
        if user is not None:
            login(request, user)
            return redirect('get_your_goods:welcome')
        else:
            return render(
                request,
                'get_your_goods/login.html', 
                {'error': 'Invalid credentials'})

    return render(request, 'get_your_goods/login.html')


def logout_user(request):
    logout(request)
    return redirect('get_your_goods:login')


def build_invoice_email(user, invoice):
    subject = "Your Get Your Goods Invoice"

    user_email = user.email

    # You can replace this with settings.EMAIL_HOST_USER later
    domain_email = "example@domain.com"

    email = EmailMessage(
        subject,
        invoice,
        domain_email,
        [user_email]
    )

    return email


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def welcome(request):
    if request.user.groups.filter(name="Vendors").exists():
        return render(request, "get_your_goods/vendor_welcome.html")

    return render(request, "get_your_goods/buyer_welcome.html")


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def create_store(request):
    if not request.user.groups.filter(name="Vendors").exists():
        return HttpResponseForbidden("Only vendors can create stores.")
    
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        Store.objects.create(
            vendor=request.user,
            name=name,
            description=description
        )

        return redirect("get_your_goods:view_stores")

    return render(request, "get_your_goods/create_store.html")


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def view_stores(request):
    stores = Store.objects.filter(vendor=request.user)

    return render(
        request,
        "get_your_goods/view_stores.html",
        {"stores": stores},
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)

    if request.method == "POST":
        store.name = request.POST.get("name")
        store.description = request.POST.get("description")
        store.save()

        return redirect("get_your_goods:view_stores")

    return render(request, "get_your_goods/edit_store.html", {"store": store})


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def delete_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)

    if request.method == "POST":
        store.delete()
        return redirect("get_your_goods:view_stores")

    return render(request, "get_your_goods/delete_store.html",
                  {"store": store})


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def create_product(request):
    if not request.user.groups.filter(name="Vendors").exists():
        return HttpResponseForbidden("Only vendors can create stores.")
    
    stores = Store.objects.filter(vendor=request.user)

    if request.method == "POST":

        store = Store.objects.get(id=request.POST.get("store"))

        Product.objects.create(
            store=store,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            price=request.POST.get("price"),
            stock=request.POST.get("stock"),
        )

        return redirect("get_your_goods:view_products")

    return render(request,
                  "get_your_goods/create_product.html",
                  {"stores": stores},
                  )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def view_products(request):

    products = Product.objects.filter(
        store__vendor=request.user
    )

    return render(
        request,
        "get_your_goods/view_products.html",
        {"products": products},
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def edit_product(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        store__vendor=request.user
    )

    stores = Store.objects.filter(vendor=request.user)

    if request.method == "POST":
        product.store = Store.objects.get(id=request.POST.get("store"))
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.save()

        return redirect("get_your_goods:view_products")

    return render(
        request,
        "get_your_goods/edit_product.html",
        {
            "product": product,
            "stores": stores,
        },
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def delete_product(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        store__vendor=request.user
    )

    if request.method == "POST":
        product.delete()
        return redirect("get_your_goods:view_products")

    return render(
        request,
        "get_your_goods/delete_product.html",
        {"product": product},
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def store_detail(request, store_id):
    store = get_object_or_404(
        Store,
        id=store_id,
        vendor=request.user
    )

    products = Product.objects.filter(store=store)

    return render(
        request,
        "get_your_goods/store_detail.html",
        {
            "store": store,
            "products": products,
        }
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def browse_products(request):
    products = Product.objects.all()

    return render(
        request,
        "get_your_goods/browse_products.html",
        {"products": products},
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    product_id = str(product.id)

    if product_id in cart:
        if cart[product_id] < product.stock:
            cart[product_id] += 1
    else:
        if product.stock > 0:
            cart[product_id] = 1

    request.session["cart"] = cart

    return redirect("get_your_goods:browse_products")


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def view_cart(request):
    cart = request.session.get("cart", {})

    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        total += subtotal

        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(
        request,
        "get_your_goods/view_cart.html",
        {
            "items": items,
            "total": total,
        },
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def increase_quantity(request, product_id):
    cart = request.session.get("cart", {})

    product = get_object_or_404(Product, id=product_id)
    product_id = str(product_id)

    if product_id in cart:
        if cart[product_id] < product.stock:
            cart[product_id] += 1

    request.session["cart"] = cart

    return redirect("get_your_goods:view_cart")


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def decrease_quantity(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session["cart"] = cart

    return redirect("get_your_goods:view_cart")


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart

    return redirect("get_your_goods:view_cart")


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("get_your_goods:view_cart")

    # Check stock
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return render(
                request,
                "get_your_goods/checkout_failed.html",
                {"product": product},
            )

    # Build invoice
    invoice_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        subtotal = product.price * quantity
        total += subtotal

        invoice_items.append({
            "name": product.name,
            "quantity": quantity,
            "price": product.price,
            "subtotal": subtotal,
        })

    invoice = "GET YOUR GOODS\n\n"
    invoice += f"Customer: {request.user.username}\n\n"

    invoice += "Items Purchased:\n"

    for item in invoice_items:
        invoice += (
            f"{item['name']} x {item['quantity']} "
            f"- R{item['subtotal']}\n"
        )

    invoice += f"\nTotal: R{total}"

    # Deduct stock
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        product.stock -= quantity
        product.save()

        Purchase.objects.create(
            buyer=request.user,
            product=product,
            quantity=quantity,
        )

    # Send email
    email = build_invoice_email(request.user, invoice)
    email.send()

    # Empty cart
    request.session["cart"] = {}

    return render(
        request,
        "get_your_goods/checkout_success.html",
        {
            "invoice_items": invoice_items,
            "total": total,
        },
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def leave_review(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    purchased = Purchase.objects.filter(
        buyer=request.user,
        product=product
    ).exists()

    review = Review.objects.filter(
        buyer=request.user,
        product=product
    ).first()

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if review:
            # Update existing review
            review.rating = rating
            review.comment = comment
            review.verified = purchased
            review.save()
        else:
            # Create a new review
            Review.objects.create(
                product=product,
                buyer=request.user,
                rating=rating,
                comment=comment,
                verified=purchased,
            )

        return redirect("get_your_goods:browse_products")

    return render(
        request,
        "get_your_goods/leave_review.html",
        {
            "product": product,
            "review": review,
        },
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    reviews = Review.objects.filter(product=product)

    return render(
        request,
        "get_your_goods/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
        },
    )


@login_required(login_url=reverse_lazy("get_your_goods:login"))
def my_reviews(request):
    reviews = Review.objects.filter(buyer=request.user)

    return render(
        request,
        "get_your_goods/my_reviews.html",
        {
            "reviews": reviews,
        },
    )


def generate_reset_url(user):

    domain = "http://127.0.0.1:8000/"
    app_name = ""

    url = f"{domain}{app_name}reset_password/"

    token = secrets.token_urlsafe(16)

    expiry_date = timezone.now() + timedelta(minutes=5)

    ResetToken.objects.create(
        user=user,
        token=sha1(token.encode()).hexdigest(),
        expiry_date=expiry_date,
    )

    url += f"{token}/"

    return url


def build_reset_email(user, reset_url):
    subject = "Password Reset"

    body = (
        f"Hi {user.username},\n\n"
        f"Click the link below to reset your password:\n\n"
        f"{reset_url}"
    )

    email = EmailMessage(
        subject,
        body,
        "example@domain.com",
        [user.email],
    )

    return email


def forgot_password(request):

    if request.method == "POST":

        user_email = request.POST.get("email")

        try:
            user = User.objects.get(email=user_email)

            url = generate_reset_url(user)

            email = build_reset_email(user, url)

            email.send()

            return redirect("get_your_goods:login")

        except User.DoesNotExist:

            return render(
                request,
                "get_your_goods/forgot_password.html",
                {
                    "error": "No account exists with that email address."
                },
            )

    return render(
        request,
        "get_your_goods/forgot_password.html")


def reset_password(request, token):
    hashed = sha1(token.encode()).hexdigest()
    reset = get_object_or_404(
        ResetToken,
        token=hashed,
        used=False,
    )
    if reset.expiry_date < timezone.now():
        return render(
            request,
            "get_your_goods/token_expired.html",
        )
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(
                request,
                "get_your_goods/reset_password.html",
                {
                    "error": "Passwords do not match."
                },
            )
        user = reset.user
        user.set_password(password)
        user.save()

        reset.used = True
        reset.save()

        return redirect("get_your_goods:login")

    return render(
        request,
        "get_your_goods/reset_password.html",
    )

# REST API views


@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_store(request):

    if not request.user.groups.filter(name="Vendors").exists():
        return Response(
            {"error": "Only vendors can create stores."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = StoreSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(vendor=request.user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_product(request):

    # Check that the user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        return Response(
            {"error": "Only vendors can add products."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Make sure the selected store belongs to the logged-in vendor
    store_id = request.data.get("store")

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if store.vendor != request.user:
        return Response(
            {"error": "You can only add products to your own store."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_reviews(request, product_id):

    # Check that the user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        return Response(
            {"error": "Only vendors can retrieve reviews."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get the product
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check that the product belongs to the logged-in vendor
    if product.store.vendor != request.user:
        return Response(
            {"error": "You can only view reviews for your own products."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get the reviews
    reviews = Review.objects.filter(product=product)

    serializer = ReviewSerializer(reviews, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_vendor_stores(request, vendor_id):

    stores = Store.objects.filter(vendor_id=vendor_id)

    serializer = StoreSerializer(stores, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_store_products(request, store_id):

    products = Product.objects.filter(store_id=store_id)

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)


def reddit_feed(request):
    # Fetch posts from the "python" subreddit
    posts = get_reddit_posts("python")

    # Pass the posts into the template
    return render(request, "get_your_goods/reddit_feed.html",
                  {"posts": posts},)
