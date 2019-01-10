from django.shortcuts import render
from django.http.response import JsonResponse
from django.views import View

from dashboard.views import sentry_log
from ..models import ProductionExchange, Order, Bill
import traceback
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.utils import IntegrityError
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)


class ProductList(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_inventory:
            products = Order.objects.filter(is_produced=True, is_shipped=False)
            context = {
                'products': products
            }
            return render(request, 'page/product/product-list.html', context=context)

    def post(self, request):
        if request.user.profile.is_inventory:
            exchange_id = int(request.POST.get('id', None))
            order = Order.objects.get(id=exchange_id)
            new_product_exchange = ProductionExchange(
                order_id=order.id,
                quantity=order.production_amount,
                exchange_type='out',
                created_by=request.user
            )
            order.is_shipped = True
            try:
                with transaction.atomic():
                    new_product_exchange.save()
                    order.save()
            except IntegrityError:
                sentry_log()
                logger.exception(traceback.print_exc())
                return JsonResponse(False, safe=False)
            return JsonResponse(True, safe=False)


class ProductPending(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_inventory:
            orders = Order.objects.filter(is_in_production=True, is_produced=False)
            context = {
                'orders': orders
            }
            return render(request, 'page/product/product-pending.html', context=context)

    def post(self, request):
        if request.user.profile.is_inventory:
            order_id = request.POST.get('id', None)

            if order_id and order_id != '':
                pending_order = Order.objects.get(id=order_id)
                quantity = request.POST.get('quantity', None)
                quantity = int(quantity) if quantity else pending_order.amount

                if pending_order:
                    total_bill = pending_order.bill_per_production * quantity
                    pending_order.is_produced = True
                    pending_order.production_amount = quantity
                    pending_order.total_bill = total_bill

                    production_exchange = ProductionExchange(
                        order_id=order_id,
                        quantity=quantity,
                        created_by=request.user
                    )
                    try:
                        with transaction.atomic():
                            pending_order.save()
                            production_exchange.save()
                            bill, created = Bill.objects.get_or_create(
                                client_id=pending_order.client_id
                            )
                            bill.total_bill += total_bill
                            bill.save()
                    except Exception:
                        sentry_log()
                        logger.exception(traceback.print_exc())
                        return JsonResponse(False, safe=False)
            return JsonResponse(True, safe=False)


class ProductHistory(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_inventory:
            production_exchange_list = ProductionExchange.objects.all().select_related('order')
            context = {
                'production_exchange': production_exchange_list
            }
            return render(request, 'page/product/product-history.html', context=context)