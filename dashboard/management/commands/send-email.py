from django.core.management.base import BaseCommand, CommandError
from dashboard.models import UserProfile, Bill
from django.core.mail import send_mail
from django.template import loader
from ...views import get_total_generated_bill, get_total_received_bill, get_monthly_bill_data, get_monthly_transaction_history_data, get_monthly_total_stock, get_monthly_stock_history, get_monthly_job_status
from datetime import datetime


class Command(BaseCommand):
    help = 'This Command Is For Sending Monthly Email'

    def handle(self, *args, **options):
        users = UserProfile.objects.all()
        now = datetime.today()
        year = now.year
        month = now.month-1
        total_generated_bill = get_total_generated_bill(year, month)
        total_received_bill = get_total_received_bill(year, month)
        bills = get_monthly_bill_data(year, month)
        transaction_histories = get_monthly_transaction_history_data(year, month)
        pending_bills = Bill.objects.select_related('client')
        total_pending = 0
        for j in pending_bills:
            total_pending += j.pending_bill()
        jobs = get_monthly_job_status(year, month)
        materials_stock = get_monthly_total_stock(year, month)
        materials_stock_history = get_monthly_stock_history(year, month)

        for user in users:
            try:
                from_email = 'noreply@misfit.tech'
                to_email = 't.s.s.ovi@gmail.com'#user.user.email
                if user.is_admin:
                    html_message_bills = loader.render_to_string(
                        'page/email-template/billing-report.html',
                        {
                            'total_generated_bill':total_generated_bill,
                            'total_received_bill':total_received_bill,
                            'bills': bills,
                            'pending': pending_bills,
                            'transaction_histories':transaction_histories,
                            'total_pending': total_pending
                        }
                    )
                    subject = 'Monthly Billing Report'
                    message = 'Monthly Billing Report'
                    send_mail(subject, message, from_email, [to_email], fail_silently=False, html_message=html_message_bills)
                    html_message_jobs = loader.render_to_string(
                        'page/email-template/job-report.html',
                        {
                            'jobs': jobs,
                        }
                    )
                    subject = 'Monthly Job Status Report'
                    message = 'Monthly Job Status Report'
                    send_mail(subject, message, from_email, [to_email], fail_silently=True, html_message=html_message_jobs)
                    html_message_stocks = loader.render_to_string(
                        'page/email-template/stock-report.html',
                        {
                            'materials_stock': materials_stock,
                            'materials_stock_history': materials_stock_history,
                        }
                    )
                    subject = 'Monthly Stock Summery Report'
                    message = 'Monthly Stock Summery Report'
                    send_mail(subject, message, from_email, [to_email], fail_silently=True, html_message=html_message_stocks)

                # from_email = ''
                # to_email = user.user.email
                # send_mail(subject, message, from_email, to_email, fail_silently=True, html_message=html_message_bills)
                # send_mail(email.subject, 'body of the message', '', [user.user.email])

            except UserProfile.DoesNotExist:
                raise CommandError('User "%s" Does Not Have a Valid E-Mail Address' % user.user.username)