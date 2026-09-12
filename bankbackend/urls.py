from django.urls import path
from bankbackend.Controller import bank_controller

urlpatterns = [
    path('create_customer/', bank_controller.create_customer_details, name = "create customer plus account details"),
    path('transaction', bank_controller.transaction, name = "create transaction"),
    path('fund_transfer/', bank_controller.fund_transfer, name = "fund transfer from one account to another account"),
    path('report/', bank_controller.bank_report, name = "bank report")
]