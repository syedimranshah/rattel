import logging
import requests
from odoo import fields, models
from traceback import format_exception_only

_logger = logging.getLogger(__name__)

WOOCOMMERCE_API_CUSTOMERS_PATH = '/wp-json/wc/v3/customers/'
URLOPEN_TIMEOUT = 30

class Customer(models.AbstractModel):
    _description = 'Enotif WooCommerce Orders - order model'
    _name = 'enotif_woo_customer.customer'

          
    def process_notifications(self, notification_type, item_ids):
    
      processed_ids = []
      
      if notification_type == 'new_customer':               
             
        result = self.fetch_customers(item_ids)
        if 'error' in result: # cannot get data from remote website. try again on the next cron job
          return []           
    
        customers = result['customers']          
      
        fetched_ids = set()      
        for data in customers:
          customer_id = data['id']
          fetched_ids.add(customer_id);   
        not_fetched_ids = [id for id in item_ids if id not in fetched_ids]
        # some items do not exist on the remote website. delete notifications about them
        processed_ids.extend(not_fetched_ids);
    
        for data in customers:
          customer_id = data['id'] 
          try:          
            self.add_customer(data)
            processed_ids.append(customer_id);
          except Exception as e:
            _logger.error("ERROR: Enotif WooCommerce Customer module cannot pocess notification type: %s \n item_id: %s  \n error text: %s", notification_type, customer_id, format_exception_only(type(e), e))
      
      else: # unknown notification type
        processed_ids.extend(item_ids);
                  
      return processed_ids
 
 
    def add_customer(self, data):
      
      result = {}
      
      email = data.get('email').strip()     
      if not email:
        _logger.error('Enotif WooCommerce Customer module cannot create new customer "%s" without email.', address.get('first_name') + ' ' + address.get('last_name'))      
        return {}
        
      if self.env['res.partner'].search_count([('email', '=', email)]) == 0:
        create_data = {
              'type' : 'contact',
              'company_name' : data['billing']['company'] if data.get('billing') and data['billing'].get('company') else '',                        
              'name' : data.get('first_name') + ' ' + data.get('last_name'),
              'phone' : data['billing']['phone'] if data.get('billing') and data['billing'].get('phone') else '',              
              'email' : email,                             
              }
        new_customer_record = self.env['res.partner'].create(create_data)
      
        if new_customer_record:
        
          result['partner_id'] = new_customer_record.id
                  
          address = data.get('billing', {})   
          if address and (address.get('first_name') or address.get('last_name') or address.get('company')):                          
            create_data = {
                  'type' : 'invoice',
                  'parent_id' : new_customer_record.id,          
                  'name' : address.get('first_name') + ' ' + address.get('last_name'),
                  'company_name' : address.get('company'),
                  'street' : address.get('address_1'),
                  'street2' : address.get('address_2'),
                  'city' : address.get('city'),
                  'zip' : address.get('postcode'),
                  'phone' : address.get('phone'),
                  'email' : address.get('email'),                             
                  }
    
            if 'country' in address and address['country']:            
              country_id = self.env['res.country'].search([('code', '=', address['country'].upper())]).id
              if country_id:
                create_data['country_id'] = country_id
                if 'state' in address and address['state']:  
                  state_id = self.env['res.country.state'].search([('country_id', '=', country_id), ('code', '=', address['state'].upper())]).id
                  if state_id:
                    create_data['state_id'] = state_id   
      
            new_customer_invoice_address = self.env['res.partner'].create(create_data)

          address = data.get('shipping', {})      
          if address and (address.get('first_name') or address.get('last_name') or address.get('company')):  
            create_data = {
                  'type' : 'delivery',
                  'parent_id' : new_customer_record.id,
                  'name' : address.get('first_name') + ' ' + address.get('last_name'),
                  'company_name' : address.get('company'),
                  'street' : address.get('address_1'),
                  'street2' : address.get('address_2'),
                  'city' : address.get('city'),
                  'zip' : address.get('postcode'),
                  'phone' : address.get('phone'),
                  'email' : address.get('email'),                             
                  }
  
            if 'country' in address and address['country']:            
              country_id = self.env['res.country'].search([('code', '=', address['country'].upper())]).id
              if country_id:
                create_data['country_id'] = country_id
                if 'state' in address and address['state']:  
                  state_id = self.env['res.country.state'].search([('country_id', '=', country_id), ('code', '=', address['state'].upper())]).id
                  if state_id:
                    create_data['state_id'] = state_id          
                  
            new_customer_delivery_address = self.env['res.partner'].create(create_data)     

      return result
    
    
    def fetch_customers(self, customer_ids=[], params={}):
      """
        url = 'https://hottons.com/demo/wp/odp/wp-json/wc/v3/customers/?include=501,503&consumer_key=111111&consumer_secret=222222'
        result = {"customers":[{"id":4,"date_created":"2018-07-24T09:54:49","email":"test2@some.com"}]} 
      """ 
           
      record = self.env['enotif_woo.keys'].search([], limit=1)
      if not record.id:
        error_text = "Enotif WooCommerce Customer module cannot get data via WooCommerce API because the WooCommerce URL is not specified. Please set WooCommerce URL in Odoo admin panel -> Menu -> External Notifications -> WooCommerce Keys"
        _logger.warning(error_text)            
        return {'error' : 1, 'error_text': error_text}

      woocommerce_url = record.woocommerce_url
      woocommerce_api_key = record.woocommerce_api_key
      woocommerce_api_secret = record.woocommerce_api_secret
       
      result = {};

      url = woocommerce_url.rstrip("/") + WOOCOMMERCE_API_CUSTOMERS_PATH      
      
      if not params:
        customer_ids_str = ','.join(str(e) for e in customer_ids)
        params = {'include' : customer_ids_str, 'per_page':100}
        
      headers = {'User-Agent': 'odoo_enotif_request'}
      keys = (woocommerce_api_key, woocommerce_api_secret)
      
      try:     
        r = requests.get(url, params=params, auth=keys, headers=headers, timeout=URLOPEN_TIMEOUT, verify=False)
        r.raise_for_status()
        result['customers'] = r.json()
        
        totalPages = int(r.headers.get('X-WP-TotalPages', 1))       
        if totalPages > 1:
          for i in range(2, totalPages + 1):
            params['page'] = i
            r = requests.get(url, params=params, auth=keys, headers=headers, timeout=URLOPEN_TIMEOUT, verify=False)
            result['customers'].extend(r.json())                
      except Exception as e:
        error_text = "ERROR: Enotif WooCommerce Customer module cannot get data via WooCommerce API with URL %s \n error text : %s" % (url, format_exception_only(type(e), e))
        result = {'error' : 1, 'error_text': error_text}
        _logger.error(error_text)            

      return result

 
        
    def import_customers(self):
    
      result = self.fetch_customers([], {'_fields' : 'id,email', 'per_page':100})
      if 'error' in result: # cannot get data from remote website.
        return result           
  
      customers = result['customers']   
      
      number_of_customers = 0
       
      if customers:
        model_id = self.env['ir.model']._get(self._name).id
        
        local_emails = set(self.env['res.partner'].search([]).mapped('email'))
         
        ids = [c['id'] for c in customers if c['email'] not in local_emails]         
        
        Notification = self.env['enotif.notification'] 
        
        #set priority 10 so it will be processed after the live notifications from another website with default priority 5       
        Notification.save_notifications_for_type('new_customer', ids, priority=10) 
            
        Notification.schedule_fetch_notifications_cron_job()
                           
        number_of_customers = len(ids)
        
      return {'number_of_customers' : number_of_customers}
      
        
        
        
        
        
        
        
        