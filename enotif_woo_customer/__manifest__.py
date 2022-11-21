{
    'name': "Enotif WooCommerce Customer",
    'version': '15.0.1.0.0',
    'summary': """Receives notifications of new WooCommerce customers""",
    'description': """
       Receives notifications of new WooCommerce customers and saves them.
       Requires "External Notifications" and "Enotif WooCommerce" modules.                   
    """,
    'author': 'Pektsekye',
    'website': 'http://hottons.com/',
    'category': 'Website',
    'depends': ['enotif_woo',                
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/notification_types.xml',                           
        'views/view.xml'
    ],
    'demo': [], 
    'images': ['static/description/screenshot_2.png'],
    'assets': {
        'web.assets_backend': [
            'enotif_woo_customer/static/src/css/main.css',
            'enotif_woo_customer/static/src/js/main.js'
        ]
    },           
    'license': 'OPL-1',
    'support':'pektsekye@gmail.com',
    'application': False,    
    'installable': True,
    'auto_install': True,
}
