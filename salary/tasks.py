from celery import shared_task
import csv
from .models import Salary, Beneficiary, Transaction
from celery.utils.log import get_task_logger
import os
import pandas as pd

logger = get_task_logger(__name__)
  
@shared_task
def add_salary(file, ben_id, com_id):
        data = pd.read_csv(file)
        for index,row in data.iterrows():
            row = row.to_dict()
            process_row.delay(row, com_id, ben_id)

@shared_task
def process_row(row, com_id, ben_id):
    if Salary.objects.filter(employee_id=row["id"], company_id = com_id).exists():
        Salary.objects.filter(employee_id=row["id"], company_id = com_id).update(
        employee_id = row["id"],
        wallet_no = row["wallet_no"],
        amount = row["amount"],
        beneficiary_id = ben_id,
        company_id = com_id
        )
    else:
        salary = Salary.objects.create(
            employee_id = row["id"],
            wallet_no = row["wallet_no"],
            amount = row["amount"],
            beneficiary_id = ben_id,
            company_id = com_id
        )
        salary.save()

@shared_task
def disburse(ben_id, com_id):
    salaries = Salary.objects.filter(beneficiary_id = ben_id)
    logger.info(salaries)
    for salary in salaries:
        salary = {
            'employee_id': salary.employee_id,
            'wallet_no': salary.wallet_no,
            'amount': salary.amount,
        }
        disburse_one.delay(salary, com_id)
    beneficiary = Beneficiary.objects.get(id=ben_id)
    beneficiary.is_complete = True
    beneficiary.save()
       
@shared_task
def disburse_one(salary, com_id):
    transaction = Transaction.objects.create(
        employee_id = salary['employee_id'],
        wallet_no = salary['wallet_no'],
        amount = salary['amount'],
        company_id = com_id
        )
    transaction.save()