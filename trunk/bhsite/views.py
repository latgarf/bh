# Create your views here.

from django.template import loader, Context
from django.http import QueryDict, HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from bhsite.models import Transaction, Opened, ShareHolder
from bhsite.utils import getExpiryTime, getAmount, getIP
from bhsite.forms import *    # HomeForm

from bhsdk.pricing import getPremium
from bhsdk.utils import gen_query_id
from bhsdk.time import to_epoch_str, utc_now
from bhsdk.enums import TransactionStatus as TS, get_verbal_status
from bhsdk.bitcoind import BitcoindService
from bhsdk.rates import get_rate, get_realtime_rate
from bhsdk.enums import BTCUSD_CALL_SHORT, BTCUSD_PUT_SHORT, prod_str, get_verbal_insurance_type
from bhsdk import config
from bhsdk import logger_access as logger

import datetime, time
import json

NUMER_FORMAT = "{:.8f}"
USD_FORMAT =  "{:.2f}"


def future(request):
    bs = BitcoindService()
    form = SubmitForm(request.POST)

    if form.is_valid():
        address_bh = bs.get_new_address()
        rate=form.cleaned_data['rate']
        expiry=form.cleaned_data['expiry']
        product_id = BTCUSD_PUT_SHORT if form.cleaned_data['select_direction'] == '1' else BTCUSD_CALL_SHORT
        trgAmount = form.cleaned_data['amount']
        srcAmount = round(trgAmount * rate, 8)
        fee = getPremium(rate, expiry, trgAmount, product_id)

        filterargs = {
            'time_expiry': 		to_epoch_str(getExpiryTime(expiry)),
            'amount_ordered': 	trgAmount,
            'addr_user': 		form.cleaned_data['address'],
            'rate': 			rate,
            'product_id': 		prod_str(product_id)
        }

        duplicated = False
        query_id = gen_query_id()
        print(query_id)

        records = Transaction.objects.filter(**filterargs)
        if len(records) > 0:
            duplicated = True
        else:
            time_expiry = to_epoch_str(getExpiryTime(expiry))
            r = Transaction.objects.create(
                time_expiry 	= time_expiry,
                product_id 		= prod_str(product_id),
                amount_ordered 	= trgAmount,
                addr_user 		= form.cleaned_data['address'],
                addr_our 		= address_bh,
                fee_quoted 		= fee,
                rate 			= rate,
                status 			= TS.WAIT_FOR_PAYMENT,
                query_id 		= query_id
            )
            logger.info('Create order %s (query ID %s) for IP %s. New BTC address %s' %(r.order_id, r.query_id, getIP(request), address_bh))


        ord_exp_time = utc_now() + datetime.timedelta(seconds=int(config.get('orders', 'order_exp_seconds')))
        print(ord_exp_time)

        ret = {
            'duplicated': duplicated,
            'ord_exp_time': ord_exp_time.strftime('%Y-%m-%d %H:%M:%S'),
            'order_id': query_id,
            'address': address_bh
        }

        ret_json = json.dumps(ret)
        return HttpResponse(ret_json, mimetype="application/json")

    # default values
    rate = get_realtime_rate()
    ma_rate = get_rate()
    trgAmount = getAmount()
    date = utc_now().date() + datetime.timedelta(days=1)
    fee = getPremium(rate, date, trgAmount, BTCUSD_CALL_SHORT)
    fee_usd = fee * rate
    exp_time = datetime.datetime(date.year, date.month, date.day) + datetime.timedelta(hours=21)
    ret = {
        'trgAmount': NUMER_FORMAT.format(trgAmount),
        'rate': USD_FORMAT.format(rate),
        'ma_rate': USD_FORMAT.format(ma_rate),
        'date': date.strftime('%Y-%m-%d'),
        'expiry': date.strftime('%Y-%m-%d %H:%M'),
        'fee': NUMER_FORMAT.format(fee),
        'fee_usd': USD_FORMAT.format(fee_usd),
        'form': form
    }

    return render(request, 'home.htm', ret)


def pay_fee_view(request):
    return render(request, 'pay_fee.htm');


@csrf_exempt
def premium(request):
    fee, fee_usd, srcAmount, rate = 0,0,0,0
    form = HomeForm(request.POST)
    if form.is_valid():
        trade_amount=form.cleaned_data['amount']
        closing_date=form.cleaned_data['expiry']
        rate = form.cleaned_data['rate']
        direction = int()
        product_id = BTCUSD_PUT_SHORT if form.cleaned_data['select_direction'] == '1' else BTCUSD_CALL_SHORT
        # srcAmount = round(trade_amount * rate, 8)
        fee = getPremium(rate, closing_date, trade_amount, product_id)
        fee_usd = fee * rate

    json_data = json.dumps({'fee_usd': USD_FORMAT.format(fee_usd), 'fee': NUMER_FORMAT.format(fee), 'rate': USD_FORMAT.format(rate)})
    # json data is just a JSON string now.
    return HttpResponse(json_data, mimetype="application/json")


@csrf_exempt
def validate_address(request):
    ret = 0
    form = HomeForm(request.POST)
    if(request.method == 'POST'):
        address = request.POST['address']
        if address:
            bs = BitcoindService()
            if bs.validate_address(address):
                ret = 1
    return HttpResponse(json.dumps({'is_valid': ret}), mimetype="application/json")


@csrf_exempt
def query(request):
    if(request.method == 'POST'):
        order_id = request.POST['order_id']
        filterargs = {'query_id': order_id}
        opened = Opened.objects.filter(**filterargs)

        if opened:
            o = opened[0]
            o.payment_sent = 0.0
            o.payment_received = 0.0
            ret = {
            'order_id': o.query_id,
            'time_ordered': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(o.time_ordered))),
            'insurance_type': get_verbal_insurance_type(o.product_id),
            'expiry': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(o.time_expiry))),
            'amount': round( float(o.amount_opened), 8),
            'addr_user': o.addr_user,
            'fee_quoted': round( float(o.fee_quoted), 8),
            'payment_received': round( float(o.payment_received), 8),
            'payment_sent': round( float(o.payment_sent), 8),
            'rate': round( float(o.rate), 2),
            'status_verbal': get_verbal_status(int(o.status))
            }

        else:
            submitted = Transaction.objects.filter(**filterargs)
            if submitted:
                i = submitted[0]
                i.payment_sent = 0.0
                i.payment_received = 0.0
                ret = {
	                'order_id': i.query_id,
	                'time_ordered': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(i.time_ordered))),
	                'insurance_type': get_verbal_insurance_type(i.product_id),
	                'expiry': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(i.time_expiry))),
	                'amount': float(i.amount_ordered),
	                'addr_user': i.addr_user,
	                'fee_quoted': float(i.fee_quoted),
	                'rate': float(i.rate),
	                'status_verbal': get_verbal_status(int(i.status))
	            }
            else:
                ret = {'order_id': ''}

        return HttpResponse(json.dumps(ret), mimetype="application/json")

    return render(request, 'query_order.htm')



@csrf_exempt
def investors(request):
    if(request.method == 'POST'):
        filterargs = {'shareholder_id': request.POST['shareholder_id']}
        sh_items = ShareHolder.objects.filter(**filterargs)
        if(sh_items):
            ret = {
                'status': 0,
                'sh_id': sh_items[0].shareholder_id,
                'shares': format(int(sh_items[0].shares), ',d')
            }
        else:
            ret = {'status': 1}
        return HttpResponse(json.dumps(ret), mimetype="application/json")
    return render(request, 'shareholders.htm')


@csrf_exempt
def dtpicker(request):
    return render(request, 'dtpicker.htm')

@csrf_exempt
def experts(request):
    return render(request, 'experts.htm')

@csrf_exempt
def contact(request):
    return render(request, 'contact.htm')

@csrf_exempt
def options(request):
    return render(request, 'options.htm')

@csrf_exempt
def futures(request):
    return render(request, 'futures.htm')

@csrf_exempt
def faq(request):
    return render(request, 'faq.htm')

@csrf_exempt
def how_it_works(request):
    return render(request, 'how_it_works.htm')


@csrf_exempt
def admin(request):
    if(request.method == 'POST'):
        filterargs = {'shareholder_id': request.POST['shareholder_id']}
        sh_items = ShareHolder.objects.filter(**filterargs)
        if(sh_items):
            ret = {
                'status': 0,
                'sh_id': sh_items[0].shareholder_id,
                'shares': format(int(sh_items[0].shares), ',d')
            }
        else:
            ret = {'status': 1}
        logger.info('Shareholder request from IP %s for shareholder ID %s' % (getIP(request), filterargs['shareholder_id']))
        return HttpResponse(json.dumps(ret), mimetype="application/json")
    return render(request, 'shareholders.htm')
