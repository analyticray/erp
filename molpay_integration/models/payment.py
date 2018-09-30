import logging
import datetime
import urlparse
import hashlib

from odoo import api, fields, models
from odoo.addons.molpay_integration.controllers.main import MolPay
from odoo.tools.float_utils import float_repr
from odoo.tools import float_round
from iso3166 import countries
from iso4217 import Currency
from hashlib import md5
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AcquirerMolPay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('molpay', 'MolPay')])
    molpay_email_account = fields.Char('Email Account', groups='base.group_user')
    molpay_merchant_id = fields.Char(string='Merchant ID', required_if_provider='molpay', groups='base.group_user')
    molpay_password = fields.Char(string='Password', groups='base.group_user')
    molpay_verify_key = fields.Char(string='Verify Key', required_if_provider='molpay', groups='base.group_user')
    molpay_security_key = fields.Char(string='Security Key')

    @api.model
    def _get_molpay_urls(self, environment):
        mp_url = 'https://www.onlinepayment.com.my/MOLPay/pay/' + str(self.molpay_merchant_id) + self.molpay_security_key
        test_url = 'https://sandbox.molpay.com/MOLPay/pay/' + str(self.molpay_merchant_id) + self.molpay_security_key
        if environment == 'prod':
            return {
                'molpay_form_url':mp_url,
            }
        else:
            return {
                'molpay_form_url': test_url,
            }


    @api.multi
    def molpay_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        d_time = datetime.datetime.now()
        d_date = datetime.datetime.strptime(str(d_time) , '%Y-%m-%d %H:%M:%S.%f')
        reg_format_date = d_date.strftime("%Y-%m-%d %H:%M:%S")
        #cr = getattr(Currency, (values['currency']).name.lower()).number
        #cu = countries.get((values['partner_country']).code.lower()).numeric
        temp_molpay_tx_values = dict(values)
	cr = values['currency'].name
        cu = values['partner_country'].code
        md5_code = self._molpay_generate_shasign(values)
        order = values.get('order')
        bill_desc = order and ', '.join([line.product_id.description_sale for line in order.order_line if line.product_id.description_sale]) or ''

        temp_molpay_tx_values.update({
            'amount' : float_repr(float_round(values['amount'], 2),2),
            'orderid' : values['reference'],
            'bill_name' : values.get('billing_partner_name'),
            'bill_email' : values.get('billing_partner_email'),
            'bill_mobile' : values.get('billing_partner_phone'),
            'bill_desc' : bill_desc,
            'country' : cu or '',
            'returnurl' : '%s' % urlparse.urljoin(base_url, MolPay._return_url),
            'callbackurl': '%s' % urlparse.urljoin(base_url, MolPay._callback_url),
            'cancelurl' : '%s' % urlparse.urljoin(base_url, MolPay._cancel_url),
            'vcode' : md5_code,
            'cur': cr or '',
	'merchant_id':self.molpay_merchant_id,
            'langcode' : values.get('billing_partner_lang'),
        })
        print">>>>>>>>>molpay_form_generate_values>>>>>>>>>>>>>>",temp_molpay_tx_values
        s_amount = "?amount=" + float_repr(float_round(values['amount'], 2),2)
        s_order = "orderid=" + values['reference']
        bill_desc = "bill_desc="+bill_desc
        s_vcode = "vcode=" + md5_code
        self.molpay_security_key = '&'.join([
            s_amount,
            s_order,
            bill_desc,
            s_vcode
        ])
        return temp_molpay_tx_values

    def _molpay_generate_shasign(self, values):

        """ Generate the shasign for incoming or outgoing communications.

        :param string inout: 'in' (odoo contacting molpay) or 'out' (molpay
                             contacting odoo). In this last case only some
                             fields should be contained (see e-Commerce basic)
        :param dict values: transaction values

        :return string: shasign
        """
        assert self.provider == 'molpay'
        trans_key = self.molpay_verify_key
        merchant = self.molpay_merchant_id
        amount = float_repr(float_round(values['amount'], 2), 2)
        data = ''.join([
            amount,
            merchant,
            values['reference'],
            trans_key])
        m = hashlib.md5()
        m.update(data.encode("utf-8"))
        return m.hexdigest()

    @api.multi
    def molpay_get_form_action_url(self):
        return self._get_molpay_urls(self.environment)['molpay_form_url']


class PaymentTransactionMolpay(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _molpay_form_get_tx_from_data(self, data):
        reference = data.get('orderid')
        transaction = self.search([('reference', '=', reference)])
        return transaction

    @api.multi
    def _molpay_form_validate(self, data):
        status = data.get('status')
        transaction_status = {
            '00': {
                'state': 'done',
                'acquirer_reference': data.get('CrossReference'),
                'state_message': data.get('extraP') or _('MolPay: feedback error'),
                'date_validate': datetime.datetime.strptime(data.get('paydate'), '%Y-%m-%d %H:%M:%S'),
            },
            '22': {
                'state': 'pending',
                'acquirer_reference': data.get('CrossReference'),
                'state_message': data.get('extraP') or _('MolPay: feedback error'),
                'date_validate': datetime.datetime.strptime(data.get('paydate'), '%Y-%m-%d %H:%M:%S'),
            },
            '11': {
                'state': 'error',
                'acquirer_reference': data.get('CrossReference'),
                'state_message': '{}:{}'.format(data.get('error_code'),data.get('error_desc')) or _('MolPay: feedback error'),
                'date_validate': datetime.datetime.strptime(data.get('paydate'), '%Y-%m-%d %H:%M:%S'),
            },
#            '20': {
#                'state': 'error',
#                'state_message': data.get('extraP') or _('MolPay: feedback error'),
#                'acquirer_reference': data.get('CrossReference'),
#                'date_validate': datetime.datetime.strptime(data.get('paydate'), '%Y-%m-%d %H:%M:%S'),
#            },
#            '30': {
#                'state': 'error',
#                'state_message': data.get('extraP') or _('MolPay: feedback error'),
#                'acquirer_reference': data.get('CrossReference'),
#                'date_validate': datetime.datetime.strptime(data.get('paydate'), '%Y-%m-%d %H:%M:%S'),
#            }

        }
        vals = transaction_status.get(status, False)
        if not vals:
            vals = transaction_status['30']
            _logger.info(vals['state_message'])
        x = self.write(vals)
        return x

