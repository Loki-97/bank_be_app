from django.db import models

class CustomerDetails(models.Model):
    name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=100)
    email = models.EmailField()
    acc_type = models.CharField(max_length=100)
    acc_number = models.CharField(max_length=100)
    acc_balance = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)

class Transactions(models.Model):
    trans_type = models.CharField(max_length=100)
    customer = models.ForeignKey(CustomerDetails, on_delete=models.CASCADE)
    customer_acc_no = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2)
    debit = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2)


