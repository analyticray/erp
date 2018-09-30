import json
import logging
import pprint
import urllib2
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MolPay(http.Controller):
    _callback_url = '/payment/molpay/callback/'
    _return_url = '/payment/molpay/return/'
    _cancel_url = '/payment/molpay/cancel/'
    _notify_url ='/payment/molpay/notification/'
	

    def __init__(self):
         print">>>>>>>>>>>>>init>>>>>>>>>>>>>"
         _logger.info(
            'molpay: File Called')
    
    @http.route(_return_url, type='http', auth='none', methods=['POST','GET'], csrf=False)
    def molpay_return(self, **post):
        """ MolPay."""
	print "==========================_return_url,========",post,self
        _logger.info(
            'molpay: entering form_feedback(return) with post data %s', pprint.pformat(post))
        return_url = '/'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'molpay')
        return werkzeug.utils.redirect(post.pop('return_url', '/shop/payment/validate'))
    
    @http.route(_notify_url, type='http', auth='none', methods=['POST','GET'], csrf=False)
    def molpay_notify(self, **post):
        """ MolPay."""
	print "*************************post",post
        _logger.info(
            'molpay: entering form_feedback(return) with post data %s', pprint.pformat(post))
        return_url = '/'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'molpay')
        return werkzeug.utils.redirect(post.pop('return_url', '/shop/payment/validate'))

    @http.route(_callback_url, type='http', auth='none', methods=['POST','GET'], csrf=False)
    def molpay_callback(self, **post):
	print "<VDFVFVFvffffe333333333333333333333",post
        """ MolPay."""
        _logger.info(
            'molpay: entering form_feedback(callback) with post data %s', pprint.pformat(post))
        return_url = '/'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'molpay')
        return werkzeug.utils.redirect(post.pop('return_url', '/shop/payment/validate'))

    @http.route(_cancel_url, type='http', auth="none", csrf=False)
    def molpay_cancel(self, **post):
        """ MolPay."""
        _logger.info(
            'molpay: entering(cancel) form_feedback with post data %s', pprint.pformat(post))
        return_url = '/'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'molpay')
        return werkzeug.utils.redirect(post.pop('return_url', '/shop/payment/validate'))

