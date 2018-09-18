import logging
import datetime
import urlparse
import hashlib

from odoo import api, fields, models
from odoo.addons.payment_iPay88.controllers.main import iPay88
from odoo.tools.float_utils import float_repr
from odoo.tools import float_round
from iso3166 import countries
from iso4217 import Currency
from hashlib import md5
from odoo import api, fields, models, _
from datetime import datetime

_logger = logging.getLogger(__name__)


class AcquireriPay88(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('ipay88', 'iPay88')])
    ipay88_merchant_code = fields.Char(string='Merchant Code', required_if_provider='ipay88', groups='base.group_user')
    ipay88_merchant_key = fields.Char(string='Merchant Key', required_if_provider='ipay88', groups='base.group_user')
    ipay88_login = fields.Char('Login', groups='base.group_user')
    ipay88_password = fields.Char(string='Password', groups='base.group_user')

    @api.model
    def _get_ipay88_urls(self):
        url = 'https://payment.ipay88.com.my/epayment/entry.asp'
        return {
            'ipay88_form_url':url,
        }


    @api.multi
    def ipay88_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        d_time = datetime.now()
        d_date = datetime.strptime(str(d_time) , '%Y-%m-%d %H:%M:%S.%f')
        cr = (values['currency']).name
        cu = countries.get((values['partner_country']).code.lower()).numeric
        temp_ipay88_tx_values = dict(values)
        signature = self._ipay88_generate_shasign(values)
        order = values.get('order')
        prod_desc = order and ', '.join([line.product_id.description_sale for line in order.order_line if line.product_id.description_sale]) or ''
        temp_ipay88_tx_values.update({
            'MerchantCode':self.ipay88_merchant_code,
            'amount' : float_repr(float_round(values['amount'], 2),2),
            'refno' : values['reference'],
            'user_name' : values.get('billing_partner_name'),
            'email' : values.get('billing_partner_email'),
            'bill_mobile' : values.get('billing_partner_phone'),
            'prod_desc' : prod_desc,
            'country' : cu or '',
            'ResponseURL' : '%s' % urlparse.urljoin(base_url, iPay88._response_url),
            'BackendURL': '%s' % urlparse.urljoin(base_url, iPay88._backend_url),
            'signature' : signature,
            'currency': cr or '',
            'langcode' : values.get('billing_partner_lang'),
        })
        print">>>>>>>>>ipay88_form_generate_values>>>>>>>>>>>>>>",temp_ipay88_tx_values
        return temp_ipay88_tx_values

    def _ipay88_generate_shasign(self, values):

        """ Generate the shasign for incoming or outgoing communications.

        :param string inout: 'in' (odoo contacting ipay88) or 'out' (ipay88
                             contacting odoo). In this last case only some
                             fields should be contained (see e-Commerce basic)
        :param dict values: transaction values

        :return string: shasign
        """
        assert self.provider == 'ipay88'
        merchant_key = self.ipay88_merchant_key
        merchant_code = self.ipay88_merchant_code
        amount = float_repr(float_round(values['amount'], 2), 2)
        amount = amount.replace('.','').replace(',','')
        data = ''.join([
            merchant_key,
            merchant_code,
            values['reference'],
            amount,
            values['currency'].name
        ] )
        m = hashlib.sha256()
        m.update(data.encode("utf-8"))
        return m.hexdigest()

    @api.multi
    def ipay88_get_form_action_url(self):
        return self._get_ipay88_urls()['ipay88_form_url']


class PaymentTransactionipay88(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _ipay88_form_get_tx_from_data(self, data):
        reference = data.get('RefNo')
        transaction = self.search([('reference', '=', reference)])
        return transaction

    @api.multi
    def _ipay88_form_validate(self, data):
        status = data.get('Status')
        bank_name = data.get('S_bankname')
        cc_name = data.get('CCName')
        ccno = data.get('CCNo')
        transaction_status = {
            '0': {
                'state': 'error',
                'acquirer_reference': data.get('TransId'),
                'state_message': data.get('ErrDesc') or _('ipay88: feedback error'),
                'date_validate': fields.Datetime.now(),
            },
            '1': {
                'state': 'done',
                'acquirer_reference': data.get('TransId'),
                'state_message': '{}:{}:{}'.format(bank_name,cc_name,ccno) or _('ipay88: feedback error'),
                'date_validate': fields.Datetime.now(),
            },
        }
        vals = transaction_status.get(status, False)
        if not vals:
            vals = transaction_status['0']
            _logger.info(vals['state_message'])
        x = self.write(vals)
        return x

