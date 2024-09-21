from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm, ChangePasswordFrom, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.http import JsonResponse
from django.db.models import Q
import json
from cart.cart import Cart


@require_GET
def auto_complete(request):
    searched = request.GET['query']
    results = Product.objects.filter(
        Q(name__icontains=searched) | Q(description__icontains=searched))

    suggestions = []
    for product in results:
        suggestions.append({'value': product.name, 'data': product.id})

    return JsonResponse({"suggestions": suggestions})


@require_POST
def search(request):
    searched = request.POST['searched']
    if searched != '':
        searched = Product.objects.filter(
            Q(name__icontains=searched) | Q(description__icontains=searched))

    if not searched:
        messages.error(request, "Product does not exist")
        return render(request, "search.html", {})
    else:
        return render(request, "search.html", {'searched': searched})


@login_required
@require_http_methods(['GET', 'POST'])
def update_info(request):
    current_user = Profile.objects.get(user__id=request.user.id)
    shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=current_user)
        shipping_form = ShippingForm(request.POST, instance=shipping_user)
    else:
        form = UserInfoForm(instance=current_user)
        shipping_form = ShippingForm(instance=shipping_user)
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})

    result1 = form.is_valid()
    if result1:
        form.save()
        messages.success(request, "User/billing information has been updated")
    else:
        errors = list(form.errors.values())
        if errors:
            messages.error(request, "Issue(s) found with provided user/billing information")
            for error in errors:
                messages.error(request, error)

    result2 = shipping_form.is_valid()
    if result2:
        shipping_form.save()
        messages.success(request, "Shipping information has been updated")
    else:
        errors = list(shipping_form.errors.values())
        if errors:
            messages.error(request, "Issue(s) found with provided shipping information")
            for error in errors:
                messages.error(request, error)

    if not result1 or not result2:
        return render(request, 'update_info.html',
                      {'form': form, 'shipping_form': shipping_form})
    else:
        return redirect('home')


@login_required
def update_password(request):
    current_user = request.user
    if request.method == 'POST':
        form = ChangePasswordFrom(current_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password successfully updated")
            login(request, current_user)
            return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return redirect('update_password')
    else:
        form = ChangePasswordFrom(current_user)
        return render(request, "update_password.html", {'form': form})


@login_required
def update_user(request):
    current_user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=current_user)
    else:
        user_form = UpdateUserForm(instance=current_user)

    if user_form.is_valid():
        user_form.save()
        login(request, current_user)
        messages.success(request, "User has been updated")
        return redirect('home')
    else:
        for error in list(user_form.errors.values()):
            messages.error(request, error)
        return render(request, 'update_user.html', {'user_form': user_form})


def category_summary(request):
    return render(request, 'category_summary.html', {})


def category(request, name):
    name = name.replace('-', ' ')
    try:
        category = Category.objects.get(name=name)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products,
                                                 'category': category})
    except Category.DoesNotExist:
        messages.error(request, "Category does not exist.")
        return redirect('home')


def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


def about(request):
    return render(request, 'about.html', {})


def login_user(request):
    if 'next' in request.GET:
        messages.add_message(request, messages.INFO,
                             'Must be logged in to access that page')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            current_user = Profile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart

            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)

                for id, qty in converted_cart.items():
                    cart.db_add(id, qty)

            messages.success(request, "Successfully logged in")
            return redirect('home')
        else:
            messages.error(request, "There was an error, please try again")
            return redirect('login')
    else:
        if request.user.is_authenticated:
            messages.error(request, "Already logged in")
            return redirect('home')
        else:
            return render(request, 'login.html', {})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Account created. Please fill out the information below")
            return redirect('update_info')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return redirect('register')

    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})
