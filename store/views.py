from django.shortcuts import render, redirect
from .models import Product, Category
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
# from django import forms
from django.contrib.auth.decorators import login_required


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})


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
    categories = Category.objects.all()
    return render(request, 'home.html', {'products': products,
                                         'categories': categories})


def about(request):
    return render(request, 'about.html', {})


def login_user(request):
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
            messages.success(request, "Successfully registered. Welcome!")
            return redirect('home')
        else:
            error_list = form.errors
            for error_sub in error_list.values():
                for error in error_sub:
                    messages.error(request, error)
            return redirect('register')

    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})
