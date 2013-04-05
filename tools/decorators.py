# -*- coding: utf-8 -*-
from google.appengine.api import users

from tools.common import decode

def login_required(func):
    """You can use the @login_required decorator to disallow access to specific
    BaseRequestHandler methods (eg. get(), post()). Example:

        class Secrets(BaseRequestHandler):
            @login_required
            def post(self):
                self.render("secrets.html")

    """
    def _wrapper(request, *args, **kw):
        if request.userprefs:
            return func(request, *args, **kw)
        else:
            """
            return request.redirect( \
                    users.create_login_url(request.request.uri))
            """
            target_url = "/account?continue=%s" % \
                decode(request.get('continue'))

            action = decode(request.get('action'))
            if action and action == "verify":
                fid = decode(request.get('openid_identifier'))
                url = users.create_login_url(target_url, federated_identity=fid)
                request.redirect(url)
            else:
                # BaseRequestHandler provides .render() for rendering a template
                request.render("login.html", {"continue_to": target_url})

    return _wrapper

def admin_required(func):
    
    def _wrapper(request, *args, **kw):
        if users.is_current_user_admin():
            return func(request, *args, **kw)
        else:
            return request.redirect(users.create_login_url(request.request.url))
            
    return _wrapper
