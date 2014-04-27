from django.db import models
from django import forms
from django.contrib.auth.models import User
from bhsdk.time import now_epoch_str
import uuid

CURRENCY_CHOICES = (
    ('USD', 'USD'),
    ('BTC', 'BTC'),
)

# Deprecated !!
# class FutureTransaction(models.Model):
# 	user_address = models.CharField(max_length=128)
# 	# receive_address = models.CharField(max_length=128)
# 	due_date = models.DateTimeField()
# 	# ts = models.DateTimeField() # When transaction happens
# 	price = models.FloatField()
# 	amount = models.FloatField()
# 	settlement_price = models.FloatField()
# 	# fee = models.FloatField()
# 	# status = models.IntegerField()

class Transaction(models.Model):
    time_ordered = models.CharField(max_length=14, default=now_epoch_str)
    product_id = models.CharField(max_length=4)
    time_expiry = models.CharField(max_length=14)
    amount_ordered = models.DecimalField(decimal_places=8, max_digits=12)
    addr_user = models.CharField(max_length=32)
    addr_our = models.CharField(max_length=32)
    fee_quoted = models.DecimalField(decimal_places=8, max_digits=12)
    rate = models.DecimalField(decimal_places=2, max_digits=6)
    status = models.IntegerField()
    order_id = models.CharField(max_length=32, primary_key=True, default=uuid.uuid4)
    query_id = models.CharField(max_length=32)

    class Meta:
        db_table = 'submitted'

    def __unicode__(self):
        return unicode(self.owner) + '\'s contract at ' + unicode(self.creation_date)

class Opened(models.Model):
    time_ordered = models.CharField(max_length=14, default=now_epoch_str)
    product_id = models.CharField(max_length=4, default='0001')
    time_expiry = models.CharField(max_length=14)
    amount_ordered = models.DecimalField(decimal_places=8, max_digits=12)
    addr_user = models.CharField(max_length=32)
    addr_our = models.CharField(max_length=32)
    fee_quoted = models.DecimalField(decimal_places=8, max_digits=12)
    rate = models.DecimalField(decimal_places=2, max_digits=6)
    status = models.IntegerField()
    order_id = models.CharField(max_length=32, primary_key=True, default=uuid.uuid4)
    query_id = models.CharField(max_length=32)
    time_opened = models.CharField(max_length=14, blank=True)
    payment_received = models.DecimalField(null=True, max_digits=12, decimal_places=8, blank=True)
    amount_opened = models.DecimalField(null=True, max_digits=12, decimal_places=8, blank=True)
    time_closed = models.CharField(null=True, max_length=14, blank=True)
    time_paid = models.CharField(null=True, max_length=14, blank=True)
    payment_sent = models.DecimalField(null=True, max_digits=12, decimal_places=8, blank=True)
    class Meta:
        db_table = 'opened'

class ShareHolder(models.Model):
    shareholder_id = models.CharField(max_length=32, primary_key=True)
    shares = models.IntegerField()

    class Meta:
        db_table = 'share_registry'
