from django.shortcuts import render
from django.http.response import HttpResponseRedirect, JsonResponse
from django.views import View
from django.core.urlresolvers import reverse
from django.contrib import messages
from ..models import Client
from django.contrib.auth.mixins import LoginRequiredMixin
import traceback
import logging
from dashboard.views import sentry_log

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ClientList(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            context = {
                'active': 2,
                'clients': Client.objects.filter(is_deleted=False)
            }
            return render(request, 'page/client/client-list.html', context=context)


class ClientCreate(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            return render(request, 'page/client/client-add.html', {'active': 2})

    def post(self, request):
        try:
            Client.objects.create(
                name=request.POST.get('name', None),
                email=request.POST.get('email', None),
                phone_no=request.POST.get('phone', None),
                address=request.POST.get('address', None),
                created_by=request.user
            )
            if '_save' in request.POST:
                messages.add_message(request, messages.SUCCESS, "Client Added Successfully")
                return HttpResponseRedirect(reverse('client'))
            if '_save_and_add' in request.POST:
                messages.add_message(request, messages.SUCCESS, "Client Added Successfully")
                return HttpResponseRedirect(reverse('client-create'))

        except Exception:
            sentry_log()
            logger.exception(traceback.print_exc())
            messages.add_message(request, messages.WARNING, "Failed to Add Client")
            return HttpResponseRedirect(reverse('client-create'))


class ClientUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            context = {
                'active': 2,
                'client': Client.objects.get(id=pk)
            }
            return render(request, 'page/client/client-update.html', context=context)

    def post(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            try:
                client = Client.objects.get(id=pk)
                client.name = request.POST.get('name', None)
                client.email = request.POST.get('email', None)
                client.phone_no = request.POST.get('phone', None)
                client.address = request.POST.get('address', None)
                client.save()
                messages.add_message(request, messages.SUCCESS, "Updated Client")
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Update Client")
            return HttpResponseRedirect(reverse('client'))


class ClientDelete(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            try:
                client = Client.objects.get(id=pk)
                client.is_deleted = True
                client.save()
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                return JsonResponse({'success': False})
            return JsonResponse({'success': True})
