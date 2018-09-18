import json
import logging
import pprint
import urllib2
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class iPay88(http.Controller):
    _backend_url = '/payment/iPay88/callback/'
    _response_url = '/payment/iPay88/return/'

    def __init__(self):
         _logger.info(
            'ipay88: File Called')
    
    @http.route(_response_url, type='http', auth='none', methods=['POST'], csrf=False)
    def ipay88_return(self, **post):
        """ ipay88."""
        _logger.info(
            'ipay88: entering form_feedback(return) with post data %s', pprint.pformat(post))
        return_url = '/'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'ipay88')
        return werkzeug.utils.redirect(post.pop('return_url', '/shop/payment/validate'))
    
    @http.route(_backend_url, type='http', auth='none', methods=['POST'], csrf=False)
    def ipay88_callback(self, **post):
        """ ipay88."""
        _logger.info(
            'ipay88: entering form_feedback(callback) with post data %s', pprint.pformat(post))
        return_url = '/'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'ipay88')
        return werkzeug.utils.redirect(post.pop('return_url', '/shop/payment/validate'))

