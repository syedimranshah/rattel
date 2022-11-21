
from odoo import http
from odoo.http import request

class Customer(http.Controller):

                        
    @http.route(['/enotif_woo_customer/import_customers/'], type="json", methods=['POST', 'GET'], auth="user", website=True)
    def import_customers(self, **kw):
 
        result = request.env['enotif_woo_customer.customer'].import_customers()

        return result

        