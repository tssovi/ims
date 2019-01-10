from django.shortcuts import render
from django.http.response import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.http import urlencode
from ..models import Order, SubMaterial, Inventory, Material, Client, OrderQuantity, InventoryRequirement
import traceback
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
import logging
from weasyprint import HTML
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from dashboard.views import sentry_log

# Get an instance of a logger
logger = logging.getLogger(__name__)


class OrderList(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            orders = Order.objects.all().select_related('client')
            context = {
                'active': 1,
                'orders': orders,
            }
            return render(request, 'page/order/order-list.html', context=context)


class OrderCreate(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:

            available_materials = set(Inventory.objects.filter(
                available_weight__gt=0
            ).select_related(
                'sub_material__material'
            ).values_list('sub_material__material'))

            materials = Material.objects.filter(is_deleted=False, id__in=[i[0] for i in available_materials])

            context = {
                'active': 4,
                'materials': materials,
                'clients': Client.objects.filter(is_deleted=False)
            }
            return render(request, 'page/order/order-add.html', context=context)

    def post(self, request):
        if request.user.profile.is_admin:
            try:
                structure_list = request.POST.getlist('structure', None)
                new_order = Order(
                    purchase_order=request.POST.get('po', None),
                    name=request.POST.get('job_name', None),
                    client_id=int(request.POST.get('client', None)),
                    amount=request.POST.get('quantity', None),
                    bill_per_production=request.POST.get('bpi', None),
                    delivery_date=request.POST.get('delivery_date', None),
                    created_by=request.user
                )
                try:
                    with transaction.atomic():
                        new_order.save()
                        for i in structure_list:
                            OrderQuantity.objects.create(
                                order=new_order,
                                material_id=i,
                                created_by=request.user
                            )
                except Exception:
                    sentry_log()
                    logger.exception(traceback.print_exc())
                    messages.add_message(request, messages.WARNING, "Failed to Add Order")
                    return redirect('order-create')

                if '_save' in request.POST:
                    path = reverse('order-update', kwargs={'pk': new_order.id})
                    params = urlencode({'message': 'Order Added Successfully'})
                    url = "%s?%s" % (path, params)
                    return redirect(url)
                if '_save_and_add' in request.POST:
                    messages.add_message(request, messages.SUCCESS, "Order Added Successfully")
                    return redirect('order-create')

            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Add Order")
                return redirect('order-create')


class OrderUpdate(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if request.user.profile.is_admin:
            if 'pk' in kwargs:
                materials = Order.objects.get(pk=kwargs['pk']).orderquantity_set.filter(required_quantity=0)
                message = request.GET.get('message', None)
                if message:
                    messages.add_message(request, messages.SUCCESS, message)
                context = {
                    'active': 4,
                    'order': Order.objects.get(pk=kwargs['pk']),
                    'materials': materials,
                    'inventory': Inventory.objects.all().select_related('sub_material').filter(available_weight__gt=0),
                    'sub_materials': SubMaterial.objects.filter(is_deleted=False).select_related('material'),
                }
                return render(request, 'page/order/order-update.html', context=context)

    def post(self, request, **kwargs):
        if request.user.profile.is_admin:
            data = request.POST
            order_id, material_id, quantity, sub_material_id, inventory, stock = kwargs['pk'], None, None, None, {}, []
            for k, v in data.items():
                if k == 'material-id':
                    material_id = v
                elif k == 'weight':
                    quantity = v
                elif k == 'sub-material-id':
                    sub_material_id = v
                elif k.startswith('take_stock_'):
                    stock.append(int(k.split('_')[-1]))
                elif k.startswith('requirement'):
                    inventory_id = int(k.split('_')[1])
                    inventory[inventory_id] = v

            try:
                with transaction.atomic():
                    count=0
                    oq = OrderQuantity.objects.get(
                        order_id=order_id,
                        material_id=material_id
                    )
                    oq.required_quantity = quantity
                    oq.sub_material_id = sub_material_id
                    # oq.save()
                    for i in stock:
                        InventoryRequirement.objects.create(
                            order_quantity=oq,
                            inventory_id=i,
                            required_quantity=inventory[i]
                        )
                        count = count + 1
                    if count == len(stock) and len(stock) > 0:
                        oq.save()
                        return JsonResponse({'success': True})
                    else:
                        return JsonResponse({'success': False})
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                return JsonResponse({'success': False})
            # return JsonResponse({'success': True})


class OrderEdit(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            context = {
                'active': 2,
                'order': Order.objects.get(id=pk),
                'clients': Client.objects.filter(is_deleted=False)
            }
            return render(request, 'page/order/order-edit.html', context=context)

    def post(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            try:
                order = Order.objects.get(id=pk)
                order.purchase_order = request.POST.get('po', None)
                order.name = request.POST.get('job_name', None)
                order.client_id = int(request.POST.get('client', None))
                order.amount = request.POST.get('quantity', None)
                order.bill_per_production = request.POST.get('bpi', None)
                order.delivery_date = request.POST.get('delivery_date', None)
                order.save()
                messages.add_message(request, messages.SUCCESS, "Updated Order")
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Update Order")
            return HttpResponseRedirect(reverse('order'))


class JobCardDownload(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.is_finance:
            pk = kwargs['pk']
            order = Order.objects.get(id=pk)
            job_no = order.job_card_number
            try:
                with open(settings.JOB_TARGET + 'job_card_' + job_no + '.pdf', 'rb') as pdf:
                    pdf_data = pdf.read()
                    response = HttpResponse(pdf_data, content_type='application/pdf')
                    return response
            except Exception:
                order_qty = OrderQuantity.objects.filter(order_id=order.id).select_related('material', 'sub_material')
                client = Client.objects.get(id=order.client_id)
                create_date = order.created_at.strftime("%A %d, %B %Y")
                delivery_date = order.delivery_date.strftime("%A %d, %B %Y")
                sentry_log()
                logger.exception(traceback.print_exc())
                return create_pdf(order, order_qty, client, job_no, create_date, delivery_date)


def create_pdf(order, order_qty, client, job_no, create_date, delivery_date):
    html_string = render_to_string(
        'page/job.html', {
            'order': order,
            'order_qty': order_qty,
            'client': client,
            'job_no': job_no,
            'create_date': create_date,
            'delivery_date': delivery_date
        }
    )

    html = HTML(string=html_string)
    html.write_pdf(target=settings.JOB_TARGET + 'job_card_' + job_no + '.pdf')

    fs = FileSystemStorage(settings.JOB_TARGET)

    with fs.open(settings.JOB_TARGET + 'job_card_' + job_no + '.pdf', 'rb') as pdf:
        pdf_data = pdf.read()
        response = HttpResponse(pdf_data, content_type='application/pdf')
        return response
