from django.contrib import admin
from .models import Order, Material, SubMaterial, Client, UserProfile

admin.site.register(Order)
admin.site.register(Material)
admin.site.register(SubMaterial)
admin.site.register(Client)
admin.site.register(UserProfile)
