{
    'name': 'iPay88 Malaysian Payment Gateway',
    'summary': 'Payment gateway integration of iPay88',
    'author': 'AnalytiCray',
	'price': '90',
	'currency': 'EUR',
	'license': 'Other proprietary',
'category': 'Payment',
    'description': """
Payment gateway integration of iPay88.
""",
    'website': '',
    'depends': ['payment','website_sale'],
    'data': [
	        'view/ipay88.xml',
            'view/ipay88_template.xml',
            'data/payment_acquirer_data.xml'],

    'installable': True,

}
