{
    'name': "External Notifications",
    'version': '15.0.1.0.0',
    'summary': """Receives notifications from another website""",
    'description': """
       Provides a way to receive notifications from another website.
       By default this module does nothing.
       It is used by another modules that have methods to connect and to process a certain notification.
       For example it is used by enotif_woo module that receives notifications from WooCommerce of new customers, orders.                    
    """,
    'author': 'Syed',
    'category': 'Website',
    'depends': ['base',
                'website'
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',                   
        'views/view.xml'
    ],
    'demo': [],
    'images': ['static/description/screenshots/ScreenShot.png'],
    'assets': {
        'web.assets_backend': [
            'enotif/static/src/css/main.css',
            'enotif/static/src/js/main.js'
        ]
    },               
    'license': 'LGPL-3',
    'application': True,    
    'installable': True,
    'auto_install': False,
}
