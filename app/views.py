# planner/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm
from .models import Transaction, UserProfile
from django.contrib import messages

def index(request):
    return render(request, 'app/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.profile.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'app/register.html', {'form': form})

@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = income - expense

    context = {
        'transactions': transactions,
        'income': income,
        'expense': expense,
        'balance': balance,
    }
    return render(request, 'app/dashboard.html', context)

from .models import Transaction
from django import forms

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'category','from_to', 'note']

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "Transaction added.")
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'app/add_transaction.html', {'form': form})


@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app/transaction_list.html', {'transactions': transactions})


@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    messages.success(request, "Transaction deleted.")
    return redirect('transaction_list')

@login_required
def user_list(request):
    users = UserProfile.objects.select_related('user').all()
    print(users)
    return render(request, 'app/user_list.html', {'users': users})

@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserRegisterForm()
    return render(request, 'app/create_user.html', {'form': form})

@login_required
def update_user(request):
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfile, id=request.POST.get('user_id'))
        user = user_profile.user
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        user_profile.phone_number = request.POST.get('phone_number')
        user_profile.save()
        return redirect('user_list')

def delete_user(request, pk):
    user_profile = get_object_or_404(UserProfile, pk=pk)
    user_profile.user.delete()
    return redirect('user_list')