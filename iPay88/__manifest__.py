{
    'name': 'iPay88 Payment Gateway Integration',
    'summary': 'Payment Gateway Integration of iPay88',
	 'author': 'AnalytiCray',
	'price': '90',
	'currency': 'EUR',
	'license': 'Other proprietary',
'category': 'Payment',
    'description': """
Payment gateway integration of iPay88.
""",
    'website': 'https://analyticray.com',
    'depends': ['payment','website_sale'],
    'data': [
	        'view/ipay88.xml',
            'view/ipay88_template.xml',
            'data/payment_acquirer_data.xml'],
    'images': ['static/description/banner.png'],
    'installable': True,

}
