from django.shortcuts import render
from django.http.response import HttpResponseRedirect, JsonResponse
from django.views import View
from django.core.urlresolvers import reverse
from django.contrib import messages
from ..models import Material, SubMaterial, Requisition
from django.contrib.auth.mixins import LoginRequiredMixin
import traceback
import logging
from dashboard.views import sentry_log

# Get an instance of a logger
logger = logging.getLogger(__name__)


class MaterialList(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            context = {
                'active': 3,
                'materials': Material.objects.filter(is_deleted=False)
            }
            return render(request, 'page/material/material-list.html', context=context)


class MaterialCreate(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            return render(request, 'page/material/material-add.html', {'active': 3})

    def post(self, request):
        if request.user.profile.is_admin:
            try:
                name = request.POST.get('name', None)
                type = request.POST.get('type', None)
                Material.objects.create(
                    name=name,
                    type=type,
                    created_by=request.user
                )
                if '_save' in request.POST:
                    messages.add_message(request, messages.SUCCESS, name + " Added Successfully")
                    return HttpResponseRedirect(reverse('material'))
                if '_save_and_add' in request.POST:
                    messages.add_message(request, messages.SUCCESS, name + " Added Successfully")
                    return HttpResponseRedirect(reverse('material-create'))

            except Exception:
                messages.add_message(request, messages.WARNING, "Failed to Add Material")
                return HttpResponseRedirect(reverse('material-create'))


class MaterialUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            context = {
                'active': 3,
                'material': Material.objects.get(id=pk)
            }
            return render(request, 'page/material/material-update.html', context=context)

    def post(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            try:
                material = Material.objects.get(id=pk)
                material.name = request.POST.get('name', None)
                material.save()
                messages.add_message(request, messages.SUCCESS, "Updated Material")
            except Exception:
                messages.add_message(request, messages.WARNING, "Failed to Update Material")
            return HttpResponseRedirect(reverse('material'))


class MaterialDelete(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            try:
                material = Material.objects.get(id=pk)
                material.is_deleted = True
                material.save()
            except Exception:
                return JsonResponse({'success': False})
            return JsonResponse({'success': True})


class SubMaterialList(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            context = {
                'active': 3,
                'sub_materials': SubMaterial.objects.filter(is_deleted=False).select_related('material')
            }
            return render(request, 'page/sub-material/sub-material-list.html', context=context)


class SubMaterialCreate(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            context = {
                'active': 3,
                'materials': Material.objects.all()
            }
            return render(request, 'page/sub-material/sub-material-add.html', context=context)

    def post(self, request):
        if request.user.profile.is_admin:
            try:
                name = request.POST.get('name', None)
                SubMaterial.objects.create(
                    material_id=int(request.POST.get('material', None)),
                    name=name,
                    code=request.POST.get('code', None),
                    created_by=request.user
                )
                if '_save' in request.POST:
                    messages.add_message(request, messages.SUCCESS, name + " Added Successfully")
                    return HttpResponseRedirect(reverse('sub-material'))
                if '_save_and_add' in request.POST:
                    messages.add_message(request, messages.SUCCESS, name + " Added Successfully")
                    return HttpResponseRedirect(reverse('sub-material-create'))

            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Add Sub Material")
                return HttpResponseRedirect(reverse('sub-material-create'))


class SubMaterialUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            context = {
                'active': 3,
                'sub_material': SubMaterial.objects.get(id=pk),
                'materials': Material.objects.all()
            }
            return render(request, 'page/sub-material/sub-material-update.html', context=context)

    def post(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            try:
                sm = SubMaterial.objects.get(id=pk)
                sm.name = request.POST.get('name', None)
                sm.code = request.POST.get('code', None)
                sm.save()
                messages.add_message(request, messages.SUCCESS, "Updated Sub Material")
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Update Sub Material")
            return HttpResponseRedirect(reverse('sub-material'))


class SubMaterialDelete(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.user.profile.is_admin:
            pk = kwargs['pk']
            try:
                sm = SubMaterial.objects.get(id=pk)
                sm.is_deleted = True
                sm.save()
            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                return JsonResponse({'success': False})
            return JsonResponse({'success': True})


class SubMaterialOrder(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.profile.is_admin:
            context = {
                'sub_materials': SubMaterial.objects.filter(is_deleted=False)
            }
            return render(request, 'page/sub-material/sub-material-order.html', context=context)

    def post(self, request):
        if request.user.profile.is_admin:
            try:
                Requisition.objects.create(
                    sub_material_id=int(request.POST.get('sub_material', None)),
                    order_quantity=int(request.POST.get('quantity', None)),
                    created_by=request.user
                )
                if '_save' in request.POST:
                    messages.add_message(request, messages.SUCCESS, "Order Added Successfully")
                    return HttpResponseRedirect(reverse('sub-material'))
                if '_save_and_add' in request.POST:
                    messages.add_message(request, messages.SUCCESS, "Order Added Successfully")
                    return HttpResponseRedirect(reverse('sub-material-order'))

            except Exception:
                sentry_log()
                logger.exception(traceback.print_exc())
                messages.add_message(request, messages.WARNING, "Failed to Add Sub Material")
                return HttpResponseRedirect(reverse('sub-material-order'))
