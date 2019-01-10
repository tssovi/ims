from django.shortcuts import render
from django.http.response import HttpResponseRedirect, JsonResponse
from .models import UserProfile, Client, Order, Bill, TransactionHistory, ProductionExchange, Inventory, InventoryExchange, NotificationSeen
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import Sum, F
from datetime import datetime, timedelta, date
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def user_login(request):
    if request.method == "GET":
        return render(request, 'page/login.html')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to index page.
                return HttpResponseRedirect(reverse('dashboard'))
            else:
                # Return a 'disabled account' error message
                return HttpResponse("Your account is disabled.")
        else:
            # Return an 'invalid login' error message.
            return HttpResponse("Invalid details")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@login_required
def calendar(request):
    if request.user.profile.is_admin:
        orders = Order.objects.all()
        productions = ProductionExchange.objects.all().select_related('order')
        bills = TransactionHistory.objects.all().select_related('client')

        context = {
            'orders': orders,
            'productions': productions,
            'bills': bills
        }
        return render(request, 'page/calendar.html', context=context)


@login_required
def dashboard(request):
    if request.user.profile.is_admin:
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        previous_days = request.GET.get('previous_days', None)

        today = date.today()

        total_pending_bills = Bill.objects.all().aggregate(pending=Sum('total_bill')-Sum('received_bill'))
        inventory = Inventory.objects.values('status').annotate(total=Sum('available_weight'))

        todays_clients = Client.objects.filter(created_at__startswith=today).count()
        todays_orders = Order.objects.filter(created_at__startswith=today).count()
        todays_product_ready = ProductionExchange.objects.filter(exchange_date__startswith=today, exchange_type='in').count()
        todays_bills = TransactionHistory.objects.all().filter(exchange_date__startswith=today).count()

        if start_date:
            todays_clients = Client.objects.filter(created_at__gte=start_date).count()
            todays_orders = Order.objects.filter(created_at__gte=start_date).count()
            todays_product_ready = ProductionExchange.objects.filter(exchange_date__gte=start_date, exchange_type='in').count()
            todays_bills = TransactionHistory.objects.all().filter(exchange_date__gte=start_date).count()
        if end_date:
            todays_clients = Client.objects.filter(created_at__lte=end_date).count()
            todays_orders = Order.objects.filter(created_at__lte=end_date).count()
            todays_product_ready = ProductionExchange.objects.filter(exchange_date__lte=end_date, exchange_type='in').count()
            todays_bills = TransactionHistory.objects.all().filter(exchange_date__lte=end_date).count()
        if previous_days:
            start_date = (datetime.now() - timedelta(days=int(previous_days))).date()
            end_date = today
            todays_clients = Client.objects.filter(created_at__range=(start_date, end_date)).count()
            todays_orders = Order.objects.filter(created_at__range=(start_date, end_date)).count()
            todays_product_ready = ProductionExchange.objects.filter(exchange_date__range=(start_date, end_date), exchange_type='in').count()
            todays_bills = TransactionHistory.objects.all().filter(exchange_date__range=(start_date, end_date)).count()

        low_materials = Inventory.objects.select_related('sub_material').values(
                            'sub_material', 'sub_material__name'
                        ).annotate(
                            left=Sum('available_weight')
                        ).filter(left__lte=1000)
        high_pending = Bill.objects.select_related('client').values(
                            'client', 'client__name'
                        ).annotate(
                            bill=Sum('total_bill'),
                            rcv=Sum('received_bill'),
                            pending=Sum('total_bill') - Sum('received_bill')
                        ).filter(pending__gte=10000).order_by('-pending')
        context = {
            'pending_bill': total_pending_bills,
            'inventory': inventory,
            'todays_clients': todays_clients,
            'todays_orders': todays_orders,
            'todays_product_ready': todays_product_ready,
            'todays_bills': todays_bills,
            'low_materials': low_materials,
            'high_pending': high_pending,
            'user_profile': UserProfile.objects.get(user=request.user)
        }
        return render(request, 'page/dashboard.html', context=context)


@login_required
def bill_summary(request):
    if request.user.profile.is_admin:
        if request.method == 'GET':
            bills = Bill.objects.filter(total_bill__gt=F('received_bill')).select_related('client')
            context = {
                'bills': bills
            }
            return render(request, 'page/dashboard/bill-summary.html', context=context)


@login_required
def material_summary(request):
    if request.user.profile.is_admin:
        if request.method == 'GET':
            materials = Inventory.objects.select_related('sub_material').values(
                'sub_material', 'sub_material__name'
            ).annotate(
                total_weight=Sum('available_weight')
            ).filter(
                total_weight__gt=0
            ).order_by('-total_weight')

            context = {
                'materials': materials,

            }
            return render(request, 'page/dashboard/material-summary.html', context=context)


@login_required
def job_summary(request):
    if request.user.profile.is_admin:
        if request.method == 'GET':
            start_date = request.GET.get('start_date', None)
            end_date = request.GET.get('end_date', None)
            client_id = request.GET.get('client_id', None)

            jobs = Order.objects.select_related('client').values(
                'client', 'client__name'
            ).annotate(
                total_shipped=Sum('is_shipped'),
                total_produced=(Sum('is_produced') - Sum('is_shipped')),
                total_in_production=(Sum('is_in_production') - Sum('is_produced'))
            )

            if start_date:
                jobs = jobs.filter(created_at__gt=start_date)
            if end_date:
                jobs = jobs.filter(created_at__lt=end_date)
            if client_id:
                jobs = jobs.filter(client_id=client_id)

            clients = Client.objects.filter(is_deleted=False)
            context = {
                'jobs': jobs,
                'clients': clients
            }
            return render(request, 'page/dashboard/job-summary.html', context=context)


@login_required
def notification_seen(request):
    NotificationSeen.objects.filter(user=request.user).update(has_seen=True)
    return JsonResponse({'success': True})


@login_required
def monthly_billing_email(request):
    if request.user.profile.is_admin:
        now = datetime.today()
        year = now.year
        month = now.month-1
        total_generated_bill = get_total_generated_bill(year, month)
        total_received_bill = get_total_received_bill(year, month)
        bills = get_monthly_bill_data(year, month)
        transaction_histories = get_monthly_transaction_history_data(year, month)
        pending_bills = Bill.objects.select_related('client')
        total_pending = 0                                   # Bill.objects.annotate(total_pending=Sum('pending_bill()'))
        for j in pending_bills:
            total_pending += j.pending_bill()
        context = {
            'total_generated_bill': total_generated_bill,
            'total_received_bill': total_received_bill,
            'bills': bills,
            'pending': pending_bills,
            'transaction_histories': transaction_histories,
            'total_pending': total_pending
        }
        return render(request, 'page/email-template/billing-report.html', context=context)


def get_monthly_bill_data(year, month):
    bills = TransactionHistory.objects.filter(
        exchange_date__year=year, exchange_date__month=month).select_related('client').values(
        'client', 'client__name'
    ).annotate(total_received_amount=Sum('received_amount'))
    return bills


def get_monthly_transaction_history_data(year, month):
    transaction_histories = TransactionHistory.objects.filter(
        exchange_date__year=year, exchange_date__month=month).select_related('client').order_by('-exchange_date')
    return transaction_histories


def get_total_generated_bill(year, month):
    total_generated_bill = Order.objects.filter(
        created_at__year=year, created_at__month=month
    ).aggregate(total_generated_bill = Sum('total_bill'))
    return total_generated_bill


def get_total_received_bill(year, month):
    total_received_bill = TransactionHistory.objects.filter(
        exchange_date__year=year, exchange_date__month=month
    ).aggregate(total_received_bill = Sum('received_amount'))
    return total_received_bill

# def get_total_pending_bill(year, month):
#     total_pending_bill = Order.objects.filter(
#         created_at__year=year, created_at__month=month
#     ).aggregate(total_pending_bill = Sum('total_bill'))
#     return total_pending_bill


@login_required
def monthly_stock_email(request):
    if request.user.profile.is_admin:
        now = datetime.today()
        year = now.year
        month = now.month-1
        materials_stock = get_monthly_total_stock(year, month)
        materials_stock_history = get_monthly_stock_history(year, month)
        context = {
            'materials_stock': materials_stock,
            'materials_stock_history': materials_stock_history
        }
        return render(request, 'page/email-template/stock-report.html', context=context)


def get_monthly_total_stock(year, month):
    materials_stock = Inventory.objects.filter(
        created__year=year, created__month=month).select_related('sub_material').values(
        'sub_material__name', 'status'
    ).annotate(
        total_weight=Sum('available_weight')).order_by('-total_weight')
    return materials_stock


def get_monthly_stock_history(year, month):
    materials_stock_history = InventoryExchange.objects.filter(
        exchange_date__year=year, exchange_date__month=month).select_related('stock', 'stock__sub_material')
    return materials_stock_history


@login_required
def monthly_job_email(request):
    if request.user.profile.is_admin:
        now = datetime.today()
        year = now.year
        month = now.month
        jobs = get_monthly_job_status(year, month)
        context = {
            'jobs': jobs,
        }
        return render(request, 'page/email-template/job-report.html', context=context)


def get_monthly_job_status(year, month):
    jobs = Order.objects.filter(created_at__year=year, created_at__month=month).select_related('client').order_by('-created_at')
    return jobs


def sentry_log():
    from decouple import config
    ENVIRONMENT = config('ENVIRONMENT')
    if ENVIRONMENT == "PRODUCTION":
        from raven.contrib.django.raven_compat.models import client
        client.captureException()