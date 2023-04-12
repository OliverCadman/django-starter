from django.test import SimpleTestCase


from app import calc

class CalcTest(SimpleTestCase):

    def test_calculation(self):

        res = calc.calculate(5, 6)
        self.assertEqual(res, 11)