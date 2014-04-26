# Create your views here.

from django.http import HttpResponse
import json


def query_cost(request):
    ret = {
        'status': 0,
        'value': 1
    }
    return HttpResponse(json.dumps(ret), content_type='application/json')

def query_cost_test(request):
    start_time = request.GET.get('start_time')
    start_rate = request.GET.get('start_rate')
    amount = request.GET.get('amount')
    expiry = request.GET.get('expiry')

    if (start_time == None or
        start_rate == None or
        amount == None or
        expiry == None) :

        ret = {}
        ret['status'] = 1
        ret['message'] = 'Error found in parameters'
    else:
        ret = {
            'status': 0,
            'start_time': start_time,
            'start_rate': start_rate,
            'amount': amount,
            'expiry': expiry
        }
    return HttpResponse(json.dumps(ret), content_type='application/json')
