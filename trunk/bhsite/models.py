from django.db import models
from django import forms
from django.contrib.auth.models import User
from bhsdk.time import now_epoch_str
import uuid

CURRENCY_CHOICES = ( ('USD', 'USD'), ('BTC', 'BTC'), )

class Transaction(models.Model):
    time_ordered = models.CharField(max_length=16, default=now_epoch_str)
    product_id = models.CharField(max_length=4)
    time_expiry = models.CharField(max_length=16)
    amount_ordered = models.DecimalField(decimal_places=8, max_digits=12)
    addr_user = models.CharField(max_length=36)
    addr_our = models.CharField(max_length=36)
    fee_quoted = models.DecimalField(decimal_places=8, max_digits=12)
    rate = models.DecimalField(decimal_places=2, max_digits=6)
    status = models.IntegerField()
    order_id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    query_id = models.CharField(max_length=32)

    class Meta:
        db_table = 'submitted'

    def __unicode__(self):
        return unicode(self.owner) + '\'s contract at ' + unicode(self.creation_date)
        #  # is this outdated Python2? Should be like this? -
        # __str__(self):
        # return self.name

class Opened(models.Model):
    time_ordered = models.CharField(max_length=16, default=now_epoch_str)
    product_id = models.CharField(max_length=4, default='0001')
    time_expiry = models.CharField(max_length=16)
    amount_ordered = models.DecimalField(decimal_places=8, max_digits=12)
    addr_user = models.CharField(max_length=36)
    addr_our = models.CharField(max_length=36)
    fee_quoted = models.DecimalField(decimal_places=8, max_digits=12)
    rate = models.DecimalField(decimal_places=2, max_digits=6)
    status = models.IntegerField()
    order_id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    query_id = models.CharField(max_length=32)
    time_opened = models.CharField(max_length=16, blank=True)
    payment_received = models.DecimalField(null=True, max_digits=12, decimal_places=8, blank=True)
    amount_opened = models.DecimalField(null=True, max_digits=12, decimal_places=8, blank=True)
    time_closed = models.CharField(null=True, max_length=16, blank=True)
    time_paid = models.CharField(null=True, max_length=16, blank=True)
    payment_sent = models.DecimalField(null=True, max_digits=12, decimal_places=8, blank=True)

    class Meta:
        db_table = 'opened'

class ShareHolder(models.Model):
    shareholder_id = models.CharField(max_length=32, primary_key=True)
    shares = models.IntegerField()

    class Meta:
        db_table = 'share_registry'

class TransactionId(models.Model):
    order_id = models.CharField(max_length=36, primary_key=True)
    transaction_id= models.CharField(max_length=64)

    class Meta:
        db_table = 'transaction_ids'

class BitstampHistory(models.Model):
    trade_id = models.AutoField(primary_key=True)
    ts = models.CharField(max_length=14)
    tid= models.CharField(max_length=10)
    price = models.DecimalField(decimal_places=8, max_digits=16)
    amount = models.DecimalField(decimal_places=8, max_digits=16)

    class Meta:
        db_table = 'bitstamp_history'
