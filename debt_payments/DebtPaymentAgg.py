import configparser
import copy
from datetime import datetime, timedelta
import re, os
import requests
from requests.exceptions import HTTPError
import json
from collections import namedtuple

class DebtPlan(object):
    
    def __init__(self):
        self.debts = DebtExtractor()
        self.payment_plans = PaymentPlanExtractor()
        

    
    def enrich(self):
        for debt in self.debts.loads():
            result_obj = {}
            result_obj['id'] = debt.id
            result_obj['is_in_payment_plan'] = False
            result_obj['amount'] = debt.amount
            result_obj['metadata'] = {'payment_plan_id':None,'start_date':None,'installment_frequency':None}
            result_obj['remaining_amount'] = debt.amount
            result_obj['next_payment_due_date'] = None
            debt_payment_plan = filter(lambda rec :rec.debt_id == debt.id,self.payment_plans.loads())
            for payment_plan in debt_payment_plan:
                result_obj['is_in_payment_plan'] = True
                result_obj['metadata'].update(dict(payment_plan_id= payment_plan.id, 
                start_date=payment_plan.start_date, installment_frequency = payment_plan.installment_frequency))
                
            yield result_obj
        

 

class PaymentPlan(object):
    
    def __init__(self, debt_plans):
        self.payments = PaymentExtractor()
        self.debt_plans = debt_plans

    
    def enrich(self):
        
        
        for debt in self.debt_plans.enrich():
            plan_id = debt['metadata']['payment_plan_id']
            pmt_date = debt['metadata']['start_date']
            if  not plan_id is None :
                debt_payments = sorted(filter(lambda rec :rec.payment_plan_id == plan_id,self.payments.loads()),key=lambda rec: datetime.strptime(rec.date,'%Y-%m-%d'))
                for payment in debt_payments:
                    debt['remaining_amount'] = debt['remaining_amount']  - payment.amount
                if debt['remaining_amount'] >  0:
                    today = datetime.utcnow()
                    pmtDate = datetime.strptime(pmt_date, '%Y-%m-%d')
                    difference = today - pmtDate
                    multiplier = 7 if debt['metadata']['installment_frequency'] == 'WEEKLY' else 14
                    num_days_to_next_week = difference.days % multiplier
                    debt['next_payment_due_date'] = (datetime.utcnow() + timedelta(days=num_days_to_next_week)).strftime('%Y-%m-%d')
                    debt['remaining_amount'] = round(debt['remaining_amount']  - payment.amount, 2)
                else:
                    debt['remaining_amount'] = 0.0
            
            yield debt
    

    


class BaseExtractor(object):
    
    def __init__(self, url_label):
        self._config =  configparser.ConfigParser()
        self._config.read(os.getenv('CONFIG_PATH'))
        self.url_label = url_label
        if 'data_source' in self._config and url_label in self._config['data_source']:
            self._url = self._config['data_source'][url_label]

        if not self._url or not re.search('^http[s?]://', self._url):
            raise Exception('Invalid Format for Debt URL - can only accespt http or hrrps %s' %(self._url))
    
    def loads(self):
        try:
            resp = requests.get(self._url, stream=True)
            if not resp.encoding:
                resp.encoding = 'utf-8'
            for dict in   resp.json():
                d_result = namedtuple(self.url_label, dict.keys())(*dict.values())
                yield d_result
            
        except HTTPError:
            print(f'HTTP error occurred: {HTTPError}')
        except Exception as ex:
            print(f'Runtime  error occurred: {ex}')



class DebtExtractor(BaseExtractor):
    
    def __init__(self):
        super(DebtExtractor,self).__init__('debts')
        

class PaymentExtractor(BaseExtractor):
    
    def __init__(self):
        super(PaymentExtractor,self).__init__('payments')
        
    


class PaymentPlanExtractor(BaseExtractor):
    
    def __init__(self):
        super(PaymentPlanExtractor,self).__init__('payment_plans')
        
    




def main():
    debt_plans = DebtPlan()
    debt_plan_agg = PaymentPlan(debt_plans)

    result = []
    for debt_payment in debt_plan_agg.enrich():
        result_obj = copy.deepcopy(debt_payment)
        result_obj.pop('metadata')
        result.append(result_obj)
    
    print(json.dumps(result, indent = 4))

if __name__ == "__main__":
    main()  


