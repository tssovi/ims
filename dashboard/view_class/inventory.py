from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http.response import HttpResponseRedirect, JsonResponse
from django.views import View
from django.core.urlresolvers import reverse
from django.contrib import messages
from ..models import Material, Inventory, SubMaterial, InventoryExchange, Order, OrderQuantity, Requisition, InventoryRequirement
from django.db.models import F
import traceback
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
import logging
from datetime import datetime
from dashboard.views import sentry_log

# Get an instance of a logger
logger = logging.getLogger(__name__)


class InventoryList(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_inventory:
            stock = Inventory.objects.all().select_related('sub_material').filter(available_weight__gt=0)
            context = {
                'stock': stock,
            }
            return render(request, 'page/inventory/inventory-list.html', context=context)


class InventoryHistory(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_inventory:
            iv = InventoryExchange.objects.all().select_related('stock__sub_material')
            context = {
                'inventory_exchange': iv,
            }
            return render(request, 'page/inventory/inventory-history.html', context=context)


class InventoryExtra(View):
    def get(self, request):
        if request.user.profile.is_inventory:
            # need to setup logic for stock
            stock = Inventory.objects.filter(status='stock')
            sub_materials = SubMaterial.objects.all()
            context = {
                'stock': stock,
                'sub_materials': sub_materials
            }
            return render(request, 'page/inventory/inventory-extra.html', context=context)

    def post(self, request):
        if request.user.profile.is_inventory:
            try:
                stock = request.POST.get('stock', None)
                sub_material = request.POST.get('sub-material', None)
                weight = int(request.POST.get('weight', None))
                inventory = Inventory.objects.get(
                    id=stock
                )
                inventory.available_weight += weight
                inventory.sub_material_id = sub_material
                inventory.status = 'extra'
                inventory.save()

                if '_save' in request.POST:
                    messages.add_message(request, messages.SUCCESS, "Successfully Added The Material in Extra Stock")
                    return HttpResponseRedirect(reverse('inventory'))
                if '_save_and_add' in request.POST:
                    messages.add_message(request, messages.SUCCESS, "Successfully Added The Material in Extra Stock")
                    return HttpResponseRedirect(reverse('inventory-extra'))

            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Add The Material in Extra Stock")
                return HttpResponseRedirect(reverse('inventory-extra'))


class InventoryCreate(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_inventory:
            sub_materials = SubMaterial.objects.all().select_related('material')
            context = {
                'sub_materials': sub_materials,
                'requisition': Requisition.objects.filter(
                    order_quantity__gt=F('received_quantity')
                ).select_related('sub_material')
            }
            return render(request, 'page/inventory/inventory-create.html', context=context)

    def post(self, request):
        if request.user.profile.is_inventory:
            try:
                with transaction.atomic():
                    requisition = request.POST.get('requisition', None)
                    weight = float(request.POST.get('weight', None))
                    temp_sub_material_id = request.POST.get('sub-material', None).strip().split("_")
                    submaterialid = int(temp_sub_material_id[0])
                    material = SubMaterial.objects.filter(id=submaterialid).select_related('material').first()
                    materialtype = material.material.type
                    currstock = Inventory.objects.filter(sub_material=submaterialid).first()
                    try:
                        with transaction.atomic():
                            if currstock and materialtype == 'kg':
                                tweight = weight + float(currstock.weight)
                                aweight = weight + float(currstock.available_weight)
                                invstock = Inventory.objects.get(sub_material=submaterialid)
                                invstock.weight = tweight
                                invstock.available_weight = aweight
                                invstock.save()
                                InventoryExchange.objects.create(
                                    stock_id=invstock.id,
                                    weight=weight,
                                    exchange_type='in',
                                    created_by=request.user
                                )
                            else:
                                stock = Inventory.objects.create(
                                    requisition_id=int(requisition) if requisition and requisition != '' else None,
                                    sub_material_id=submaterialid,
                                    roll_id=request.POST.get('roll_id', None),
                                    weight=weight,
                                    available_weight=weight,
                                    created_by=request.user,
                                    type='local' if request.POST.get('type', None) else 'imported'
                                )

                                InventoryExchange.objects.create(
                                    stock_id=stock.id,
                                    weight=stock.weight,
                                    exchange_type='in',
                                    created_by=request.user
                                )
                            if requisition and requisition != '':
                                req = Requisition.objects.get(id=requisition)
                                # multiple entry bug
                                req.is_arrived = True
                                req.received_quantity += int(stock.weight)
                                req.save()
                    except Exception:
                        sentry_log()
                        logger.exception(traceback.print_exc())
                        messages.add_message(request, messages.WARNING, "Failed to Add The Material in Stock")
                        return HttpResponseRedirect(reverse('inventory-create'))

                    if '_save' in request.POST:
                        messages.add_message(request, messages.SUCCESS, "Successfully Added The Material in Stock")
                        return HttpResponseRedirect(reverse('inventory'))
                    if '_save_and_add' in request.POST:
                        messages.add_message(request, messages.SUCCESS, "Successfully Added The Material in Stock")
                        return HttpResponseRedirect(reverse('inventory-create'))
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Add The Material in Stock")
                return HttpResponseRedirect(reverse('inventory-create'))


class InventoryCheckout(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_inventory:
            unfinished_orders = InventoryRequirement.objects.filter(
                required_quantity__gt=F('checkout_quantity')
            ).select_related('inventory', 'order_quantity', 'order_quantity__order', 'order_quantity__order__client', 'order_quantity__sub_material')

            context = {
                'orders': unfinished_orders
            }
            return render(request, 'page/inventory/inventory-checkout.html', context=context)

    def post(self, request):
        if request.user.profile.is_inventory:
            ir_id = int(request.POST.get('id', None))
            quantity = request.POST.get('quantity', None)
            try:
                with transaction.atomic():
                    ir = InventoryRequirement.objects.get(id=ir_id)
                    InventoryExchange.objects.create(
                        order=ir.order_quantity.order,
                        stock=ir.inventory,
                        weight=quantity,
                        exchange_type='out',
                        created_by=request.user
                    )
                    stock = ir.inventory
                    ir.checkout_quantity = int(quantity)
                    stock.available_weight -= int(quantity)
                    stock.save()
                    ir.save()

                    production_check = OrderQuantity.objects.filter(
                        order=ir.order_quantity.order,
                    )

                    flag = True
                    for i in production_check:
                        if not flag:
                            break
                        all_ir = InventoryRequirement.objects.filter(order_quantity=i)
                        if not all_ir:
                            flag = False
                            break
                        for j in all_ir:
                            if j.required_quantity > j.checkout_quantity:
                                flag = False
                                break
                    if flag:
                        order = ir.order_quantity.order
                        job_no = datetime.now().strftime("%Y%m%d%H%M%S")
                        order.job_card_number = job_no
                        order.is_in_production = True
                        order.save()
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                return JsonResponse({'success': False})
            return JsonResponse({'success': True})
