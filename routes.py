# -*- coding: utf-8 -*-

import webapp2
import handlers

from google.appengine.ext import ndb

config = {
    'webapp2_extras.auth': {
        'user_model': 'models.User',
        'user_attributes': ['name']
    },
    'webapp2_extras.sessions': {
        'secret_key': '1H556HJ67676LML66PO67JPO8JBNPVN5O6'
    }
}

# Map url's to handlers
urls = [
    webapp2.Route(r'/', handler=handlers.Main, name="home"),
    webapp2.Route(r'/put', handler=handlers.MainHandler, name="MainHandler"),
    webapp2.Route(r'/get', handler=handlers.GetCommand, name="GetCommand"),
    webapp2.Route(r'/posting', handler=handlers.PostCommand, name="PostCommand"),
    
    
    webapp2.Route(r'/rest', handler=handlers.PostHandler, name="PostHandler"),
    webapp2.Route(r'/data', handler=handlers.GetLatestData, name="GetLatestData"),
    webapp2.Route(r'/chart', handler=handlers.GetChartData, name="GetChartData"),
    
    webapp2.Route(r'/monitor', handler=handlers.Monitor, name="monitor"),
    webapp2.Route(r'/controls', handler=handlers.controls, name="controls"),
    webapp2.Route(r'/mobile', handler=handlers.Mobile, name="mobile"),
    webapp2.Route(r'/inserttoken', handler=handlers.AddToken, name="inserttoken"),
    webapp2.Route(r'/updateRFID', handler=handlers.updateRFID, name="updateRFID"),
    webapp2.Route(r'/getRFIDUsers', handler=handlers.getRFIDUsers, name="getRFIDUsers"),

    webapp2.Route(r'/auth', handler=handlers.LoginHandler, name="login"),
    webapp2.Route(r'/register', handler=handlers.SignupHandler, name="register"),
    webapp2.Route(r'/logout', handler=handlers.LogoutHandler, name="logout"),
    
    webapp2.Route(r'/test', handler=handlers.Test, name="test"),
    webapp2.Route(r'/use', handler=handlers.Use, name="use"),
    webapp2.Route(r'/login', handler=handlers.LogIn),
    webapp2.Route(r'/_ah/login_required', handler=handlers.LogIn),
    #webapp2.Route(r'/logout', handler=handlers.LogOut, name="logout"),
    webapp2.Route(r'/account', handler=handlers.Account, name="account"),
    webapp2.Route(r'/account/setup', handler=handlers.AccountSetup, name="setup"),
    (r'.*', handlers.NotFound)
]
