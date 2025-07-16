# planner/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm
from .models import Transaction, UserProfile
from django.contrib import messages

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
