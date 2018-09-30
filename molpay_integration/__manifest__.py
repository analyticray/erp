{
    'name': 'MOLPay Payment Gateway Integration',
    'summary': 'Payment gateway integration of MOLPay',
    'author': 'AnalytiCray',
	'price': '90',
	'currency': 'EUR',
	'license': 'Other proprietary',
    'description': """
Payment gateway integration of MolPay.
""",
    'website': 'https://analyticray.com',
    'depends': ['payment','website_sale'],
#     'images': ['static/description/img1.png'],
    'data': [
	        'views/molpay.xml',
            'views/molpay_template.xml',
            'data/payment_acquirer_data.xml'],
#      'demo': [
#         'data/payment_acquirer_data.xml',
#     ],

    'installable': True,

}
