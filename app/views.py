# planner/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm
from .models import Transaction, UserProfile
from django.contrib import messages
import google.generativeai as genai # type: ignore
from django.db import connection
from django.conf import settings
from django import forms
import pandas as pd # type: ignore
import os

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
            return redirect('add_transaction')
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


# AI Report Generation View
G_api_key = os.environ['GOOGLE_API_KEY']
G_model = os.environ['GOOGLE_MODEL']

genai.configure(api_key=G_api_key)
# print(G_api_key," Gemini AI configured successfully")

def get_all_table_schemas():
    from django.db import connection
    schemas = {}
    allowed = getattr(settings, "AI_REPORT_ALLOWED_TABLES", [])

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        rows = cursor.fetchall()

    for table, col in rows:
        if not allowed or table in allowed:
            schemas.setdefault(table, []).append(col)

    return schemas


def build_schema_prompt():
    schemas = get_all_table_schemas()
    schema_text = ""
    for table, cols in schemas.items():
        schema_text += f"{table} ({', '.join(cols)})\n"
    return schema_text


def reports_from_ai(request):
    query_text = request.GET.get("user_prompt", "")

    if not query_text:
        return render(request, "app/ai_reports.html")

    schema_info = build_schema_prompt()

    prompt = f"""
    Convert this request into a PostgreSQL SELECT query:
    Request: "{query_text}"

    Available schema:
    {schema_info}

    Rules:
    - Exclude id columns.
    - Use only existing tables and columns shown above.
    - Do NOT invent new fields.
    - Exclude sensitive columns.
    - Return only plain SQL (no markdown, no explanation).
    """

    model = genai.GenerativeModel(G_model)
    response = model.generate_content(prompt)
    sql_query = response.text.strip()

    # cleanup ```sql ... ```
    if sql_query.startswith("```"):
        sql_query = sql_query.strip("`")
        sql_query = sql_query.replace("sql", "", 1).strip()



    with connection.cursor() as cursor:
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
    if not rows:
        return render(
            request,
            "app/ai_reports.html",
            {"query": query_text, "no_records": True}
        )

    return render(
        request,
        "app/ai_reports.html",
        {
            "query": query_text,
            "columns": columns,
            "rows": rows,
        },
    )   