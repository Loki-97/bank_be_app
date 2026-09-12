import json

import django.http.response
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import csrf_exempt

from bankbackend.Service.bank_service import BankService


@api_view(["POST"])

def create_customer_details(request):
    try:
        data = json.loads(request.body)
        bk_serv = BankService()
        resp = bk_serv.create_customer_service(data)
        return JsonResponse(resp, status=HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def transaction(request):
    try:
        data = json.loads(request.body)
        bk_serv = BankService()
        resp = bk_serv.transaction_service(data)
        return JsonResponse(resp, status=HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])

# fund transfer from one account to another account
def fund_transfer(request):
    try:
        data = json.loads(request.body)
        bk_serv = BankService()
        resp = bk_serv.fund_transfer_service(data)
        if type(resp) == dict:
            return JsonResponse(resp, status=HTTP_200_OK)

        return JsonResponse(list(resp), status=HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])

def bank_report(request):

    try:
        data = json.loads(request.body)
        bk_serv = BankService()
        # accessing the query parameters provided in the request.
        download = request.GET.get("download", 0)

        download = int(download)

        resp = bk_serv.bank_report_service(data, download)

        if type(resp) == dict:
            return JsonResponse(resp, status=HTTP_200_OK)
        elif type(resp) == django.http.response.StreamingHttpResponse:
            return resp
        return JsonResponse(list(resp), status=HTTP_200_OK, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
