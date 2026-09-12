import pandas as pd
import io

from django.http import StreamingHttpResponse, HttpResponse, JsonResponse

from bankbackend.models import CustomerDetails, Transactions
from bankbackend.Bank_Utility.utils import TransactionType
from datetime import datetime
class BankService:

    def create_customer_service(self, data):
        customer_account = CustomerDetails.objects.create(
            name = data["name"],
            mobile_no = data["mobile_no"],
            email = data["email"],
            acc_type = data["acc_type"],
            acc_number = data["account_number"],
            acc_balance = data["account_balance"],
            bank_name = data["bank_name"],
            branch_name = data["branch_name"]
        )

        return {
            "status": "success",
            "customer_id": customer_account.id,
            "message": "Customer Details created!"
        }

    def transaction_service(self, data):
        #cr / db
        type =  data["type"]
        amount = data["amount"]

        trans_date = data["date"]
        description = data["description"]
        # type_1_text (Credit)
        if type == TransactionType.type_1_text:
            cr_set = CustomerDetails.objects.filter(id=data["customer_id"])
            if len(cr_set) == 0:
                return {
                "status": "failed",
                "message": "Customer not found."
            }
            cr_obj = cr_set[0]

            if cr_obj.acc_balance == 0:

                ts_obj = Transactions.objects.create(
                    trans_type = TransactionType.type_1_text,
                    amount = amount,
                    date = trans_date,
                    customer_id = data["customer_id"],
                    customer_acc_no = cr_obj.acc_number,
                    description = f"{description} to {cr_obj.name}",
                    opening_balance = 0,
                    debit = 0,
                    credit = amount,
                    closing_balance = cr_obj.acc_balance
                )
                cr_obj.acc_balance += amount
                cr_obj.save()

                ts_obj.closing_balance += ts_obj.opening_balance + ts_obj.credit
                ts_obj.save()

            elif cr_obj.acc_balance > 0:

                trn_obj = Transactions.objects.create(
                    trans_type=TransactionType.type_1_text,
                    amount=amount,
                    date=trans_date,
                    customer_id=data["customer_id"],
                    customer_acc_no=cr_obj.acc_number,
                    description=f"{description} to {cr_obj.name}",
                    opening_balance= cr_obj.acc_balance,
                    debit=0,
                    credit = amount,
                    closing_balance = cr_obj.acc_balance + amount
                )
                cr_obj.acc_balance += amount
                cr_obj.save()

            return {
                "message": f"Amount {amount} successfully credited to {cr_obj.name}"
            }
        # type_2_text(debit)
        elif type == TransactionType.type_2_text:
            cr_set = CustomerDetails.objects.filter(id=data["customer_id"])
            if len(cr_set) == 0:
                return {
                    "status": "failed",
                    "message": "Customer not found."
                }
            cr_obj = cr_set[0]
            if cr_obj.acc_balance > amount:

                trans_obj = Transactions.objects.create(
                    trans_type=TransactionType.type_2_text,
                    amount=amount,
                    date=trans_date,
                    customer_id=data["customer_id"],
                    customer_acc_no=cr_obj.acc_number,
                    description = description,
                    opening_balance = cr_obj.acc_balance,
                    credit = 0,
                    debit = amount,
                    closing_balance = cr_obj.acc_balance - amount
                )
                cr_obj.acc_balance -= amount
                cr_obj.save()

                return {
                    "message": f"Amount {amount} successfully debited from {cr_obj.name}"
                }
            else:
                return {
                    "status": "failed",
                    "message": "customer's bank balance is low."
                }

        else:
            return {
                "status": "failed",
                "message": "invalid transaction type (choose credit/debit)!"
            }

    def fund_transfer_service(self, data):

        from_acc_no = data["from_acc_no"]
        to_acc_no = data["to_acc_no"]

        fund_to_transfer = data["amount"]
        trans_date = data["date"]

        if fund_to_transfer > 0:
            sender = CustomerDetails.objects.filter(acc_number = from_acc_no)
            if len(sender) == 0:
                return {
                    "status": "failed",
                    "message": "sender account not found."
                }

            receiver = CustomerDetails.objects.filter(acc_number=to_acc_no)
            if len(receiver) == 0:
                return {
                    "status": "failed",
                    "message": "receiver account not found."
                }

            sender_obj = sender[0]

            sender_balance = sender_obj.acc_balance
            receiver_obj = receiver[0]
            if sender_balance >= fund_to_transfer:

                trans_obj = Transactions.objects.create(
                    trans_type="debit",
                    amount=fund_to_transfer,
                    date=trans_date,
                    customer_id=sender_obj.id,
                    customer_acc_no=sender_obj.acc_number,
                    description = f"Fund {fund_to_transfer} transferred from {sender_obj.name} to {receiver_obj.name}",
                    opening_balance = sender_obj.acc_balance,
                    debit = fund_to_transfer,
                    credit = 0,
                    closing_balance = sender_obj.acc_balance - fund_to_transfer
                )
                sender_obj.acc_balance -= fund_to_transfer
                sender_obj.save()

                Transactions.objects.create(
                    trans_type="credit",
                    amount=fund_to_transfer,
                    date=trans_date,
                    customer_id=receiver_obj.id,
                    customer_acc_no=receiver_obj.acc_number,
                    description = f"Fund {fund_to_transfer} Received by {receiver_obj.name} from {sender_obj.name}",
                    opening_balance = receiver_obj.acc_balance,
                    debit = 0,
                    credit = fund_to_transfer,
                    closing_balance = receiver_obj.acc_balance + fund_to_transfer
                )
                receiver_obj.acc_balance += fund_to_transfer
                receiver_obj.save()

                return {
                    "status": "success",
                    "message": f"Fund {fund_to_transfer} transferred from {sender_obj.name} to {receiver_obj.name}"
                }

            else:
                return {
                    "status": "failed",
                   "message": "sender's bank balance is low."
                }

        else:
            return {
                "status": "failed",
                "message": "transfer amount should be greater than zero."
            }


    def bank_report_service(self, data, download):

        account_number = data["acc_no"]
        from_date = data["from_date"]
        to_date = data["to_date"]

        result = Transactions.objects.filter(customer_acc_no = account_number,
                                    date__range  = (from_date, to_date))
        if len(result) == 0:
            return {
                "status": "failed",
                "message": "invalid account number"
            }

        res_list = []

        for objs in result:

            customer_id = objs.customer_id
            cust_obj = CustomerDetails.objects.filter(id = customer_id)[0]
            name = cust_obj.name
            mob_no = cust_obj.mobile_no
            email = cust_obj.email
            acc_type = cust_obj.acc_type
            acc_bal = cust_obj.acc_balance
            bank_name = cust_obj.bank_name
            branch= cust_obj.branch_name

            customer_details = {
               "customer_id": objs.customer_id,
                "customer_name": name,
                "customer_mobile_number": mob_no,
                "emailId": email,
                "customer_account_number": objs.customer_acc_no,
                "account_type": acc_type,
                "account_balance": acc_bal,
                "bank_name": bank_name,
                "branch_name": branch
           }

            data = {
                "transaction_type": objs.trans_type,
                "customer_details": customer_details,
                "transaction_amount": objs.amount,
                "transaction_date": objs.date,
                "description": objs.description,
                "date_range": f"{from_date} To {to_date}",
                "opening_balance": objs.opening_balance,
                "debit": objs.debit,
                "credit": objs.credit,
                "closing_balance": objs.closing_balance
            }

            res_list.append(data)

        if download == 1:
            return self.generate_excel_report(res_list)

        return res_list


    def generate_excel_report(self, resp):
        df = pd.json_normalize(resp)
        buffer = io.BytesIO()


        columns = ['id', 'trans_type', 'customer_id', 'customer_acc_no', 'amount', 'date']
        if len(df) != 0 :

            df.insert(0, 'S.No', range(1, len(df) + 1))

            df.rename(columns={
            # 'transaction_type': 'Transaction Type',
            # 'customer_details.customer_id': 'Customer ID',
            # 'customer_details.customer_name': 'Customer Name',
            # 'customer_details.customer_mobile_number': 'Mobile Number',
            # 'customer_details.emailId': 'Email',
            'transaction_date': 'Transaction Date',
            'customer_details.customer_account_number': 'Account Number',
            'customer_details.account_type': 'Account Type',
            # 'customer_details.account_balance': 'Account Balance',
            # 'customer_details.bank_name': 'Bank Name',
            # 'customer_details.branch_name': 'Branch Name',
            # 'transaction_amount': 'Transaction Amount',

        }, inplace=True)

        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        try:
            writer.save()
        except:
            writer.close()
        buffer.seek(0)

        file_name = 'Account Number Transaction Report-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
        response = StreamingHttpResponse(buffer, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response




