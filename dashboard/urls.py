from django.conf.urls import url, include
from .views import calendar, user_login, user_logout, dashboard, bill_summary, material_summary, job_summary, notification_seen, monthly_billing_email, monthly_stock_email, monthly_job_email
from .view_class.inventory import InventoryCreate, InventoryExtra, InventoryCheckout, InventoryList, InventoryHistory
from .view_class.material import MaterialList, MaterialCreate, MaterialUpdate, MaterialDelete, SubMaterialList, SubMaterialCreate, SubMaterialUpdate, SubMaterialDelete, SubMaterialOrder
from .view_class.client import ClientList, ClientCreate, ClientUpdate, ClientDelete
from .view_class.order import OrderCreate, OrderList, OrderUpdate, OrderEdit, JobCardDownload
from .view_class.bill import BillCreate, BillList, InvoiceDownload
from .view_class.product import ProductList, ProductPending, ProductHistory


urlpatterns = [
    # Auth related URLS
    url(r'^login/$', user_login, name='login'),
    url(r'^logout/$', user_logout, name='logout'),

    url(r'^$', dashboard, name='dashboard'),

    # Dashboard related URLS
    url(r'^dashboard/', include([
        url('^bill$', bill_summary, name='bill-summary'),
        url('^material', material_summary, name='material-summary'),
        url('^job', job_summary, name='job-summary'),
    ])),


    # Client related URLs
    url(r'^client/', include([
        url(r'^$', ClientList.as_view(), name='client'),
        url(r'^new$', ClientCreate.as_view(), name='client-create'),
        url(r'^edit/(?P<pk>\d+)$', ClientUpdate.as_view(), name='client-update'),
        url(r'^delete/(?P<pk>\d+)$', ClientDelete.as_view(), name='client-delete'),
    ])),

    # Materials
    url(r'^material/', include([
        url(r'^$', MaterialList.as_view(), name='material'),
        url(r'^new$', MaterialCreate.as_view(), name='material-create'),
        url(r'^edit/(?P<pk>\d+)$', MaterialUpdate.as_view(), name='material-update'),
        url(r'^delete/(?P<pk>\d+)$', MaterialDelete.as_view(), name='material-delete'),
    ])),

    # Sub Materials
    url(r'^sub-material/', include([
        url(r'^$', SubMaterialList.as_view(), name='sub-material'),
        url(r'^new$', SubMaterialCreate.as_view(), name='sub-material-create'),
        url(r'^edit/(?P<pk>\d+)$', SubMaterialUpdate.as_view(), name='sub-material-update'),
        url(r'^delete/(?P<pk>\d+)$', SubMaterialDelete.as_view(), name='sub-material-delete'),
        url(r'^order$', SubMaterialOrder.as_view(), name='sub-material-order'),
    ])),

    # Order related URLs
    url(r'^order/', include([
        url(r'^$', OrderList.as_view(), name='order'),
        url(r'^new$', OrderCreate.as_view(), name='order-create'),
        url(r'^update/(?P<pk>\d+)$', OrderUpdate.as_view(), name='order-update'),
        url(r'^edit/(?P<pk>\d+)$', OrderEdit.as_view(), name='order-edit'),
    ])),

    # Inventory related URLs
    url(r'^inventory/', include([
        url(r'^$', InventoryList.as_view(), name='inventory'),
        url(r'^new$', InventoryCreate.as_view(), name='inventory-create'),
        url(r'^extra', InventoryExtra.as_view(), name='inventory-extra'),
        url(r'^history$', InventoryHistory.as_view(), name='inventory-history'),
        url(r'^checkout$', InventoryCheckout.as_view(), name='inventory-checkout'),
    ])),

    # Product related URLs
    url(r'^product/', include([
        url(r'^$', ProductList.as_view(), name='product'),
        url(r'pending/$', ProductPending.as_view(), name='product-pending'),
        url(r'history/$', ProductHistory.as_view(), name='product-history')
    ])),

    # Bills related URLs
    url(r'^bill/', include([
        url(r'^$', BillList.as_view(), name='bill'),
        url(r'^new', BillCreate.as_view(), name='bill-create'),

    ])),

    url('^invoice/(?P<pk>\d+)$', InvoiceDownload.as_view(), name='invoice-download'),
    url('^jobcard/(?P<pk>\d+)$', JobCardDownload.as_view(), name='job-card-download'),
    url('^calendar/$', calendar, name='calendar'),
    url('^notification-seen/$', notification_seen, name='notification_seen'),

    # Email Related URLS

    url(r'^billing/$', monthly_billing_email, name='billing'),
    url(r'^stock/$', monthly_stock_email, name='stock'),
    url(r'^job/$', monthly_job_email, name='job'),
]
