# -*- coding: utf-8 -*-
from baserequesthandler import BaseRequestHandler
from google.appengine.ext import db, db, webapp
from google.appengine.ext.webapp import template
from hashlib import md5
from models import *
from tools.common import decode
from tools.decorators import login_required, admin_required
import json
import datetime
import logging
import mc
import os
import tools.mailchimp
import webapp2
import httplib
import random

from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from google.appengine.ext import ndb
import logging
import os.path

class updateRFID(BaseRequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        self.response.out.write(data)
        if('user' in data):
            rf_users = RFUser.gql("WHERE id = :1", data['user'])
            if rf_users.count() == 1:
                instance = rf_users.get()

                if instance.status == "IN":
                    instance.status = "OUT"
                    instance.put();
                else:
                    instance.status = "IN"
                    instance.put();
            else:
                new_user = RFUser(id = data['user'] , status="IN", name = "new_user")
                new_user.put();
        else:
            self.error(403) # access denied
            return

class getRFIDUsers(BaseRequestHandler):
    def get(self):
        all_users = RFUser.all()
        self.render("users.html", {"rf_users": all_users})


class AddToken(BaseRequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        self.response.out.write(data)
        if('token' in data):
            g = Token.gql("WHERE value = :1", data['token'])
            if (g.count() == 0):
                token=Token(value=data['token'])
                token.put()
                return
        else:
            self.error(403) # access denied
            return


# Import packages from the project
class Monitor(BaseRequestHandler, BaseHandler):
    @user_required
    def get(self):
        # Render the template
        self.render("monitor.html")

class controls(BaseRequestHandler, BaseHandler):
    @user_required
    def get(self):
        # Render the template
        self.render("controls.html")

class Mobile(BaseRequestHandler, BaseHandler):
    @user_required
    def get(self):
        # Render the template
        self.render("mobile.html")

def gql_json_parser(query_obj):
    result = []
    for entry in query_obj:
        result.append(dict([(p, unicode(getattr(entry, p))) for p in entry.properties()]))
        return result

class PostHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        self.response.out.write(data)
        if('token' in data):
            g = Token.gql("WHERE value = :1", data['token'])
            if (g.count() > 0):
                info = ArduinoInfo(token = data['token'], temperature= data['temperature'],proximity = data['proximity'],ambient = data['ambient'],humidity = data['humidity'])
                info.put();
            else:
                self.error(403) # access denied
                return
        else:
            self.error(403) # access denied
            return

class GetLatestData(webapp2.RequestHandler):
    def get(self):
        data = ArduinoInfo.gql("ORDER BY date DESC LIMIT 1")
        jsonResponse = json.dumps(gql_json_parser(data))
        self.response.headers.add_header('content-type','application/json',charset='utf-8')
        self.response.out.write(jsonResponse)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        tokens = Token(value = 610526241)
        tokens = Token(value = 123)
        tokens.put()
        self.response.out.write('Hello worlds!')

class GetCommand(webapp2.RequestHandler):
    def get(self):
        data = Command.gql("ORDER BY date DESC LIMIT 1")
        instance = data.get()
        if instance:
            jsong_String= {"destination":str(instance.destination),"commands":{str(instance.sensor):str(instance.value)}}
            instance.delete()
            jsonResponse = json.dumps(jsong_String)
            self.response.headers.add_header('content-type','application/json',charset='utf-8')
            self.response.out.write(jsonResponse)
        else:
            self.error(204)

class PostCommand(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        self.response.out.write(data)
        if('token' in data):
            g = Token.gql("WHERE value = :1", data['token'])
            if (g.count() > 0):
                info = Command(token = data['token'], sensor= data['sensor'],value = data['value'],destination = data['destination'])
                info.put();
            else:
                self.error(403) # access denied
                return
        else:
            self.error(403) # access denied
            return

class GetChartData(webapp2.RequestHandler):
    def get(self):
        today = datetime.date.today()
        data = ArduinoInfo.gql("")
        chartData = []
        chartWrap = []

        if self.request.get("range") == "Last10":
            readings = []
            query = ArduinoInfo.gql("ORDER BY date DESC LIMIT 10 ")
            for info in query:
                if self.request.get("type") == "temperature":
                    readings.append(info.temperature)
                elif self.request.get("type") == "proximity":
                    readings.append(info.proximity)
                elif self.request.get("type") == "ambient":
                    readings.append(info.ambient)
                elif self.request.get("type") == "humidity":
                    readings.append(info.humidity)

            chartData = readings
            chartData.reverse()

        elif self.request.get("range") == "Last7Days":
            for i in xrange (0,7):
                daily = []
                totalReadings = 0
                count = 0
                day = today - datetime.timedelta(days=i)
                query = ArduinoInfo.gql("WHERE date >= :1 AND date < :2", day, day + datetime.timedelta(days=1))
                for info in query:
                    if self.request.get("type") == "temperature":
                        totalReadings = totalReadings + info.temperature
                    elif self.request.get("type") == "proximity":
                        totalReadings = totalReadings + info.proximity
                    elif self.request.get("type") == "ambient":
                        totalReadings = totalReadings + info.ambient
                    elif self.request.get("type") == "humidity":
                        totalReadings = totalReadings + info.humidity
                count = query.count()

                if count > 0:
                    average = totalReadings/count
                else:
                    average = 0

                daily.append(day.strftime("%m-%d-%y"))
                daily.append(average)
                chartData.append(daily)

        elif self.request.get("range") == "Last12Months":
            for i in xrange (0,12):
                monthly = []
                totalReadings = 0
                count = 0
                day = today - datetime.timedelta(i*365/12)
                day = day.replace(day=1)
                query = ArduinoInfo.gql("WHERE date >= :1 AND date < :2", day, day + datetime.timedelta(days=30))
                for info in query:
                    if self.request.get("type") == "temperature":
                        totalReadings = totalReadings + info.temperature
                    elif self.request.get("type") == "proximity":
                        totalReadings = totalReadings + info.proximity
                    elif self.request.get("type") == "ambient":
                        totalReadings = totalReadings + info.ambient
                    elif self.request.get("type") == "humidity":
                        totalReadings = totalReadings + info.humidity
                count = query.count()
                if count > 0:
                    average = totalReadings/count
                else:
                    average = 0

                monthly.append(day.strftime("%m"))
                monthly.append(average)
                chartData.append(monthly)

        chartWrap.append(chartData)

        jsonResponse = json.dumps(chartWrap)

        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers.add_header('content-type','application/json',charset='utf-8')
        self.response.out.write(jsonResponse)

#class Test(BaseRequestHandler):
#
#    @login_required
#    def get(self):
#
#        self.response.headers['Content-Type'] = 'text/plain'
#        self.response.out.write('Hello, ')

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def auth(self):
        """Shortcut to access the auth instance as a property."""
        return auth.get_auth()

    @webapp2.cached_property
    def user_info(self):
        """Shortcut to access a subset of the user attributes that are stored
        in the session.

        The list of attributes to store in the session is specified in
          config['webapp2_extras.auth']['user_attributes'].
        :returns
          A dictionary with most user information
        """
        return self.auth.get_user_by_session()

    @webapp2.cached_property
    def user(self):
        """Shortcut to access the current logged in user.

        Unlike user_info, it fetches information from the persistence layer and
        returns an instance of the underlying model.

        :returns
          The instance of the user model associated to the logged in user.
        """
        u = self.user_info
        return self.user_model.get_by_id(u['user_id']) if u else None

    @webapp2.cached_property
    def user_model(self):
        """Returns the implementation of the user model.

        It is consistent with config['webapp2_extras.auth']['user_model'], if set.
        """
        return self.auth.store.user_model

    @webapp2.cached_property
    def session(self):
        """Shortcut to access the current session."""
        return self.session_store.get_session(backend="datastore")

    def display_message(self, message):
        """Utility function to display a template with a simple message."""
        params = {
            'message': message
        }
        self.render('message.html', params)

    # this is needed for webapp2 sessions to work
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

def user_required(handler):
    """
      Decorator that checks if there's a user associated with the current session.
      Will also fail if there's no session present.
    """
    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            self.redirect(self.uri_for('login'), abort=True)
        else:
            return handler(self, *args, **kwargs)

    return check_login

# OpenID login
class LogIn(BaseRequestHandler):
    """
    Redirects a user to the OpenID login site. After successful login the user
    redirected to the target_url (via /login?continue=/<target_url>).
    """
    def get(self):
        # Wrap target url to redirect new users to the account setup step
        target_url = "/account?continue=%s" % \
                     decode(self.request.get('continue'))

        action = decode(self.request.get('action'))
        if action and action == "verify":
            fid = decode(self.request.get('openid_identifier'))
            url = users.create_login_url(target_url, federated_identity=fid)
            self.redirect(url)
        else:
            # BaseRequestHandler provides .render() for rendering a template
            self.render("login.html", {"continue_to": target_url})


# LogOut redirects the user to the GAE logout url, and then redirects to /
class LogOut(webapp.RequestHandler):
    def get(self):
        url = users.create_logout_url("/")
        self.redirect(url)

# Main page request handler
class Main(BaseRequestHandler, BaseHandler):
    @user_required
    def get(self):
        # Render the template
        self.render("index.html")


# Account page and after-login handler
class Account(BaseRequestHandler):
    """
    The user's account and preferences. After the first login, the user is sent
    to /account?continue=<target_url> in order to finish setting up the account
    (email, username, newsletter).
    """
    def get(self):
        target_url = decode(self.request.get('continue'))
        # Circumvent a bug in gae which prepends the url again
        if target_url and "?continue=" in target_url:
            target_url = target_url[target_url.index("?continue=") + 10:]

        if not self.userprefs.is_setup:
            # First log in of user. Finish setup before forwarding.
            self.render("account_setup.html", {"target_url": target_url, 'setup_uri':self.uri_for('setup')})
            return

        elif target_url:
            # If not a new user but ?continue=<url> supplied, redirect
            self.redirect(target_url)
            return

        # Render the account website
        self.render("account.html", {'setup_uri':self.uri_for('setup')})


class AccountSetup(BaseRequestHandler):
    """Initial setup of the account, after user logs in the first time"""
    def post(self):
        username = decode(self.request.get("username"))
        email = decode(self.request.get("email"))
        subscribe = decode(self.request.get("subscribe"))
        target_url = decode(self.request.get('continue'))
        target_url = target_url or self.uri_for('account')

        # Set a flag whether newsletter subscription setting has changed
        subscription_changed = bool(self.userprefs.subscribed_to_newsletter) \
            is not bool(subscribe)

        # Update UserPrefs object
        self.userprefs.is_setup = True
        self.userprefs.nickname = username
        self.userprefs.email = email
        self.userprefs.email_md5 = md5(email.strip().lower()).hexdigest()
        self.userprefs.subscribed_to_newsletter = bool(subscribe)
        self.userprefs.put()

        # Subscribe this user to the email newsletter now (if wanted). By
        # default does not subscribe users to mailchimp in Test Environment!
        if subscription_changed and webapp2.get_app().config.get('mailchimp')['enabled']:
            if subscribe:
                tools.mailchimp.mailchimp_subscribe(email)
            else:
                tools.mailchimp.mailchimp_unsubscribe(email)

        # After updating UserPrefs, redirect
        self.redirect(target_url)

class NotFound(BaseRequestHandler):
    def get(self):
        self.error404()

    def post(self):
        self.error404()

class SignupHandler(BaseRequestHandler, BaseHandler):
    def get(self):
        self.render('register.html')

    def post(self):
        user_name = self.request.get('username')
        email = self.request.get('email')
        name = self.request.get('name')
        password = self.request.get('password')
        last_name = self.request.get('lastname')

        unique_properties = ['email_address']
        user_data = self.user_model.create_user(user_name,
                                                unique_properties,
                                                email_address=email, name=name, password_raw=password,
                                                last_name=last_name, verified=False)
        if not user_data[0]: #user_data is a tuple
            self.display_message('Unable to create user for email %s because of \
        duplicate keys %s' % (user_name, user_data[1]))
            return

        user = user_data[1]
        user_id = user.get_id()

        token = self.user_model.create_signup_token(user_id)

        msg = 'Sucessfully Registered'

        self.display_message(msg)


class LoginHandler(BaseRequestHandler, BaseHandler):
    def get(self):
        self._serve_page()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        try:
            u = self.auth.get_user_by_password(username, password, remember=True,
                                               save_session=True)
            self.redirect(self.uri_for('home'))
        except (InvalidAuthIdError, InvalidPasswordError) as e:
            logging.info('Login failed for user %s because of %s', username, type(e))
            self._serve_page(True)

    def _serve_page(self, failed=False):
        username = self.request.get('username')
        params = {
            'username': username,
            'failed': failed
        }
        self.render('auth.html', params)

class LogoutHandler(BaseRequestHandler, BaseHandler):
    def get(self):
        self.auth.unset_session()
        self.redirect(self.uri_for('home'))