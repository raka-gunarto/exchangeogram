# auth.py
#
# Middleware (request wrappers) to check various authentication states

from exchangeogram import app
from functools import wraps
from flask import g, request, redirect, url_for, Response
from flask_login import current_user

# redirects to login if not authorized (for view renderer calls)
def auth_required_login(f):
    @wraps(f)
    def _auth_required(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return _auth_required    

# redirects to given URL if not authorized (for view renderer calls)
def auth_required_redirect(redirect_url):
    def _auth_required(f):
        @wraps(f)
        def __auth_required(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(redirect_url)
            return f(*args, **kwargs)
        return __auth_required
    return _auth_required

# returns 403 if not authorized (for API calls)
def auth_required_403(f):
    @wraps(f)
    def _auth_required(*args, **kwargs):
        if not current_user.is_authenticated:
            app.logger.warn("{0} tried to access a protected resource".format(request.remote_addr))
            return Response('{"err":"403 Forbidden"}', status=403, mimetype='application/json')
        return f(*args, **kwargs)
    return _auth_required

def unauth_required_redirect(redirect_url):
    def _unauth_required(f):
        @wraps(f)
        def __unauth_required(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(redirect_url)
            return f(*args, **kwargs)
        return __unauth_required
    return _unauth_required