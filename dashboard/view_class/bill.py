from django.shortcuts import render
from django.views import View
from ..models import Client, Order, TransactionHistory, Bill
from django.db.models import F
import traceback, decimal
from django.db import transaction
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
import logging
from dashboard.views import sentry_log

# Get an instance of a logger
logger = logging.getLogger(__name__)


class BillList(View):
    def get(self, request):
        if request.user.profile.is_finance:
            bills = TransactionHistory.objects.all().select_related('client').order_by('-exchange_date')
            context = {
                'active': 7,
                'bills': bills
            }
            return render(request, 'page/bill/bill-list.html', context=context)


class BillCreate(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_finance:
            start_date = request.GET.get('start_date', None)
            end_date = request.GET.get('end_date', None)
            client_id = request.GET.get('client_id', None)

            bills = Bill.objects.filter(total_bill__gt=F('received_bill')).select_related('client').order_by('-created')

            if start_date:
                bills = bills.filter(created__gte=start_date)
            if end_date:
                bills = bills.filter(created__lte=end_date)
            if client_id:
                bills = bills.filter(client_id=client_id)

            page = request.GET.get('page', 1)

            paginator = Paginator(bills, 10)
            try:
                bills = paginator.page(page)
            except PageNotAnInteger:
                bills = paginator.page(1)
            except EmptyPage:
                bills = paginator.page(paginator.num_pages)

            orders = Order.objects.filter(is_produced=True).all()
            clients = Client.objects.filter(is_deleted=False)
            context = {
                'active': 7,
                'bills': bills,
                'orders': orders,
                'clients': clients
            }
            return render(request, 'page/bill/bill-create.html', context=context)

    def post(self, request):
        if request.user.profile.is_finance:
            bill_id = request.POST.get('bill_id', None)
            received_bill = request.POST.get('quantity', None)
            try:
                with transaction.atomic():
                    bill = Bill.objects.get(id=bill_id)
                    bill.received_bill += decimal.Decimal(received_bill)
                    bill.save()
                    th = TransactionHistory.objects.create(
                        client_id=bill.client_id,
                        received_amount=received_bill,
                        created_by=request.user
                    )

                    invoiceNo = datetime.now().strftime("%Y%m%d%H%M%S")
                    date = datetime.now().strftime("%Y-%m-%d")
                    th.invoice_number = invoiceNo
                    th.save()
                    client = Client.objects.get(id=bill.client_id)
                    create_pdf(client, invoiceNo, date, received_bill)
                    return HttpResponseRedirect(reverse('bill'))

            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                return HttpResponseRedirect(reverse('bill-create'))


class InvoiceDownload(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.is_finance:
            pk = kwargs['pk']
            transaction_dtls = TransactionHistory.objects.get(id=pk)
            invoice_no = transaction_dtls.invoice_number
            try:
                with open(settings.INVOICE_TARGET + 'invoice_' + invoice_no + '.pdf', 'rb') as pdf:
                    pdf_data = pdf.read()
                    response = HttpResponse(pdf_data, content_type='application/pdf')
                    return response
            except Exception:
                client = Client.objects.get(id=transaction_dtls.client_id)
                rcvAmnt = transaction_dtls.received_amount
                execDate = transaction_dtls.exchange_date.strftime("%Y-%m-%d")
                sentry_log()
                logger.exception(traceback.print_exc())
                return create_pdf(client, invoice_no, execDate, rcvAmnt)


def create_pdf(client, invoice_no, date, rcv_amount):
    html_string = render_to_string(
        'page/invoice.html', {
            'client': client,
            'invoiceNo': invoice_no,
            'date': date,
            'rcvAmount': rcv_amount
        }
    )

    html = HTML(string=html_string)
    html.write_pdf(target=settings.INVOICE_TARGET + 'invoice_' + invoice_no + '.pdf')

    fs = FileSystemStorage(settings.INVOICE_TARGET)

    with fs.open(settings.INVOICE_TARGET + 'invoice_' + invoice_no + '.pdf', 'rb') as pdf:
        pdf_data = pdf.read()
        response = HttpResponse(pdf_data, content_type='application/pdf')
        return response
