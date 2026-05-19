from __future__ import absolute_import

from kivy.app import App


def check_connection_settings():
    """Checks QuESt settings and returns configuration for connection settings """
    app_config = App.get_running_app().config
    proxy_settings = {}

    # Proxy settings.
    if int(app_config.get('connectivity', 'use_proxy')):
        http_proxy = app_config.get('connectivity', 'http_proxy')
        https_proxy = app_config.get('connectivity', 'https_proxy')
        
        if http_proxy:
            proxy_settings['http'] = http_proxy
        if https_proxy:
            proxy_settings['https'] = https_proxy
    
    # SSL verification.
    ssl_verify = True if int(app_config.get('connectivity', 'use_ssl_verify')) else False

    return ssl_verify, proxy_settings