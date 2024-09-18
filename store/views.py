from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordFrom, UserInfoForm
# from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.db.models import Q


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
def update_info(request):
    current_user = Profile.objects.get(user__id=request.user.id)
    form = UserInfoForm(request.POST or None, instance=current_user)

    if form.is_valid():
        form.save()
        messages.success(request, "User information has been updated")
        return redirect('home')
    else:
        return render(request, 'update_info.html', {'form': form})


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
    user_form = UpdateUserForm(request.POST or None, instance=current_user)

    if user_form.is_valid():
        user_form.save()

        login(request, current_user)
        messages.success(request, "User has been updated")
        return redirect('home')
    else:
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
                             'You must be logged in to access that page')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
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
            messages.success(
                request,
                "Account created. Please fill out the information below")
            return redirect('update_info')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return redirect('register')

    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})
