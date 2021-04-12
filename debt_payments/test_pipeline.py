import unittest
import types,os
from datetime import datetime
from DebtPaymentAgg import DebtExtractor,PaymentExtractor,PaymentPlanExtractor

class TestExtractors(unittest.TestCase):

    def setUp(self):
        super().setUp()
        os.environ.update(dict(CONFIG_PATH='./debt_payments/configuration.ini'))
        self.assertEqual(os.environ["CONFIG_PATH"], "./debt_payments/configuration.ini")

   
    def test_DebtExtractor(self):
        debtEx = DebtExtractor()
        self.assertIsNotNone(debtEx)
        recs = debtEx.loads()
        self.assertFalse(None,recs)
        self.assertTrue(types.GeneratorType,recs)
        for res_obj in recs:
            self.assertIsNotNone(res_obj.id)
            self.assertIsInstance(res_obj.id,int)
            self.assertIsNotNone(res_obj.amount)
            self.assertIsInstance(res_obj.amount,(float, int))


    #"payment_plan_id": 0,
    #"amount": 51.25,
    #"date": "2020-09-29"
      
    def test_PaymentExtractor(self):
        payObj = PaymentExtractor()
        self.assertIsNotNone(payObj)
        recs = payObj.loads()
        self.assertFalse(None,recs)
        self.assertTrue(types.GeneratorType,recs)
        for res_obj in recs:
            self.assertIsNotNone(res_obj.payment_plan_id)
            self.assertIsInstance(res_obj.payment_plan_id, int)
            self.assertIsNotNone(res_obj.amount)
            self.assertIsInstance( res_obj.amount,(float, int))
            self.assertIsNotNone(res_obj.date)
            with self.assertRaises(ValueError):
                datetime.strptime(res_obj.date, '%m/%d/%Y')
            self.assertIsInstance(datetime.strptime(res_obj.date, '%Y-%m-%d'), datetime)

     # "id": 0,
    # "debt_id": 0,
    # "amount_to_pay": 102.50,
    # "installment_frequency": "WEEKLY", 
    # "installment_amount": 51.25,
    # "start_date": "2020-09-28"
    
    def test_PaymentPlanExtractor(self):
        payObj = PaymentPlanExtractor()
        self.assertIsNotNone(payObj)
        recs = payObj.loads()
        self.assertFalse(None,recs)
        self.assertTrue(types.GeneratorType,recs)
        for res_obj in recs:
            self.assertIsNotNone(res_obj.id)
            self.assertIsInstance(res_obj.id, int)
            self.assertIsNotNone(res_obj.debt_id)
            self.assertIsInstance(res_obj.debt_id, int)
            self.assertIsNotNone(res_obj.amount_to_pay)
            self.assertIsInstance(res_obj.amount_to_pay,(float,int))
            self.assertIn(res_obj.installment_frequency, ('WEEKLY','BI_WEEKLY'))
            self.assertIsNotNone(res_obj.installment_amount)
            self.assertIsInstance(res_obj.installment_amount,(float,int))
            self.assertIsNotNone(res_obj.start_date)
            self.assertIsInstance(datetime.strptime(res_obj.start_date, '%Y-%m-%d'), datetime)
            with self.assertRaises(ValueError):
                datetime.strptime(res_obj.start_date, '%m/%d/%Y')

         

if __name__ == '__main__':
    unittest.main()
