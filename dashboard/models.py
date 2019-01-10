from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


"""
Order Creation Related Models:
Order, OrderQuantity
"""


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(default=False)
    is_finance = models.BooleanField(default=False)
    is_inventory = models.BooleanField(default=False)
    is_office = models.BooleanField(default=False)
    avatar = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


class Material(models.Model):
    name = models.CharField(max_length=100, default='Untitled Material')
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=5, default='roll')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'material'


class SubMaterial(models.Model):
    code = models.CharField(max_length=10, default='')
    name = models.CharField(max_length=100, default='Untitled Material')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + '-' + self.material.name

    class Meta:
        db_table = 'sub_material'


class Client(models.Model):
    name = models.CharField(max_length=100)
    phone_no = models.CharField(null=True, blank=True, max_length=20)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(null=True, blank=True, max_length=200)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'client'


class Order(models.Model):
    purchase_order = models.CharField(max_length=100, default='Unknown PO')
    name = models.CharField(max_length=100, default='Untitled Order')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    layer = models.SmallIntegerField(default=1)
    structure = models.ManyToManyField(Material, through='OrderQuantity')
    amount = models.IntegerField(default=0)
    production_amount = models.IntegerField(default=0)
    bill_per_production = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_bill = models.FloatField(default=0)
    is_in_production = models.BooleanField(default=False)
    is_produced = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    delivery_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    job_card_number = models.CharField(max_length=100, null=True)

    def get_total_bill(self):
        if self.total_bill == int(self.total_bill):
            return int(self.total_bill)
        return self.total_bill

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'order'


class Requisition(models.Model):
    sub_material = models.ForeignKey(SubMaterial, on_delete=models.CASCADE)
    order_quantity = models.DecimalField(max_digits=16, decimal_places=2)
    is_arrived = models.BooleanField(default=False)
    received_quantity = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)

    def get_remaining_quantity(self):
        remaining = self.order_quantity - self.received_quantity
        if remaining == int(remaining):
            return int(remaining)
        return remaining

    def __str__(self):
        return self.sub_material.name

    class Meta:
        db_table = 'requisition'


class Inventory(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.SET_NULL, null=True, related_name='inventory')
    sub_material = models.ForeignKey(SubMaterial, on_delete=models.CASCADE, related_name='inventory')
    roll_id = models.CharField(max_length=50, default='')
    weight = models.DecimalField(max_digits=16, decimal_places=2)
    available_weight = models.DecimalField(max_digits=16, decimal_places=2)
    type = models.CharField(max_length=10, default='local')
    status = models.CharField(max_length=10, default='stock')
    created_by = models.ForeignKey(User)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sub_material.name + ': ' + self.roll_id

    class Meta:
        db_table = 'inventory'


class OrderQuantity(models.Model):
    order = models.ForeignKey(Order)
    material = models.ForeignKey(Material)
    sub_material = models.ForeignKey(SubMaterial, null=True)
    required_quantity = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    inventory = models.ManyToManyField(Inventory, through='InventoryRequirement')
    created_by = models.ForeignKey(User)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order.name

    class Meta:
        db_table = 'order_quantity'


class InventoryRequirement(models.Model):
    order_quantity = models.ForeignKey(OrderQuantity, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    required_quantity = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    checkout_quantity = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.inventory.sub_material.name + 'for ' + self.order_quantity.order.name

    class Meta:
        db_table = 'inventory_requirement'


class ProductionExchange(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    created_by = models.ForeignKey(User)
    exchange_type = models.CharField(max_length=10, default='in', db_index=True)
    exchange_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order.name

    class Meta:
        db_table = 'production_exchange'


class Bill(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    total_bill = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    received_bill = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def pending_bill(self):
        remaining = self.total_bill - self.received_bill
        if remaining == int(remaining):
            return int(remaining)
        return remaining

    def get_total_bill(self):
        if self.total_bill == int(self.total_bill):
            return int(self.total_bill)
        return self.total_bill

    def get_received_bill(self):
        if self.received_bill == int(self.received_bill):
            return int(self.received_bill)
        return self.received_bill

    def __str__(self):
        return self.client.name

    class Meta:
        db_table = 'bill'


class TransactionHistory(models.Model):
    received_amount = models.DecimalField(max_digits=16, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client.name

    class Meta:
        db_table = 'transaction_history'


class InventoryExchange(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    weight = models.IntegerField(default=0)
    stock = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User)
    exchange_type = models.CharField(max_length=10, default='in', db_index=True)
    exchange_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.stock.sub_material.name

    class Meta:
        db_table = 'inventory_exchange'


class Notification(models.Model):
    message = models.CharField(max_length=255)
    url = models.URLField(max_length=155)
    notifeed = models.ManyToManyField(User, through='NotificationSeen')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifier')
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

    class Meta:
        db_table = 'notification'


class NotificationSeen(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    has_seen = models.BooleanField(default=False)
    seen_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.notification.message

    class Meta:
        db_table = 'notification_seen'


def create_notification(sender, instance=None, created=False, **kwargs):
    if created:
        if sender.__name__ == 'Client':
            create_notification_template('1000', instance, '/client/')
        elif sender.__name__ == 'Material':
            create_notification_template('1000', instance, '/material/')
        elif sender.__name__ == 'SubMaterial':
            create_notification_template('1000', instance, '/sub-material/')
        elif sender.__name__ == 'Order':
            create_notification_template('1110', instance, '/order/')
        elif sender.__name__ == 'InventoryExchange':
            create_notification_template(
                '1100',
                instance,
                '/inventory/',
                str(instance.weight) + ' kg ' + instance.__str__() + ' is taken ' + instance.exchange_type + ' by ' + str(instance.created_by.username)
            )
        elif sender.__name__ == 'ProductionExchange':
            create_notification_template(
                '1100',
                instance,
                '/product/',
                str(instance.quantity) + ' amount ' + instance.__str__() + ' is taken ' + instance.exchange_type + ' by ' + str(instance.created_by.username)
            )

        elif sender.__name__ == 'TransactionHistory':
            create_notification_template(
                '1001',
                instance,
                '/bill/',
                str(instance.received_amount) + ' BDT was received from ' + instance.client.name + ' by ' + str(instance.created_by.username)
            )
        elif sender.__name__ == 'Requisition':
            create_notification_template('1110', instance, '/inventory/')


post_save.connect(create_notification)


def create_notification_template(type, instance, url, message=None):
    # bit 1 : admin
    # bit 2 : inventory
    # bit 3 : office
    # bit 4 : finance
    notification = Notification.objects.create(
        message=message if message else str(instance.created_by.username) + ' has created ' + instance.__str__(),
        url=url,
        created_by=instance.created_by
    )
    if type[0] == '1':
        user = User.objects.filter(profile__is_admin=True)
        for i in user:
            NotificationSeen.objects.get_or_create(
                notification=notification,
                user=i
            )
    if type[1] == '1':
        user = User.objects.filter(profile__is_inventory=True)
        for i in user:
            NotificationSeen.objects.get_or_create(
                notification=notification,
                user=i
            )
    if type[2] == '1':
        user = User.objects.filter(profile__is_office=True)
        for i in user:
            NotificationSeen.objects.get_or_create(
                notification=notification,
                user=i
            )
    if type[3] == '1':
        user = User.objects.filter(profile__is_finance=True)
        for i in user:
            NotificationSeen.objects.get_or_create(
                notification=notification,
                user=i
            )

# class Email(models.Model):
#     subject = models.CharField(max_length=250, null=True)
#     type = models.CharField(max_length=50, null=True)
#     is_admin = models.BooleanField(default=False)
#     is_finance = models.BooleanField(default=False)
#     is_inventory = models.BooleanField(default=False)
#     is_office = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.subject
#
#     class Meta:
#         db_table = 'email'
