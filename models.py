# -*- coding: utf-8 -*-
import logging

from hashlib import md5
from google.appengine.ext import db
from google.appengine.api import users

import mc

import time
import webapp2_extras.appengine.auth.models

from google.appengine.ext import ndb

from webapp2_extras import security

#Models a command that is going to be sent to an Arduino board
class Command(db.Model):
    token = db.IntegerProperty()
    sensor = db.StringProperty()
    value = db.StringProperty()
    destination = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

#Models a token for security access ( for post methods )
class Token(db.Model):
    value = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

#Models the RF-ID users that have RF- tags
class RFUser(db.Model):
    id = db.IntegerProperty()
    status = db.StringProperty()
    name = db.StringProperty()

#Models a arduino information such as temperature , humidity .. etc from the Ardiuno board
class ArduinoInfo(db.Model):
    """Models a data report from an arduino"""
    token = db.IntegerProperty()
    temperature = db.IntegerProperty()
    proximity = db.IntegerProperty()
    ambient = db.IntegerProperty()
    humidity = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class User(webapp2_extras.appengine.auth.models.User):
    def set_password(self, raw_password):
        """Sets the password for the current user

        :param raw_password:
            The raw password which will be hashed and stored
        """
        self.password = security.generate_password_hash(raw_password, length=12)

    @classmethod
    def get_by_auth_token(cls, user_id, token, subject='auth'):
        """Returns a user object based on a user ID and token.

        :param user_id:
            The user_id of the requesting user.
        :param token:
            The token string to be verified.
        :returns:
            A tuple ``(User, timestamp)``, with a user object and
            the token timestamp, or ``(None, None)`` if both were not found.
        """
        token_key = cls.token_model.get_key(user_id, subject, token)
        user_key = ndb.Key(cls, user_id)
        # Use get_multi() to save a RPC call.
        valid_token, user = ndb.get_multi([token_key, user_key])
        if valid_token and user:
            timestamp = int(time.mktime(valid_token.created.timetuple()))
            return user, timestamp

        return None, None

class UserPrefs(db.Model):
    """Storage for custom properties related to a user. Provides caching
    for super-fast access to the UserPrefs object.

    The BaseRequestHandler (see handlers/baserequesthandler.py and main.py)
    automatically provides the current UserPref object via self.userprefs.
    """
    # Base settings. Copied over from OpenID at first login (may not be valid)
    nickname = db.StringProperty()
    email = db.StringProperty(default="")

    # The md5 has of the email is used for gravatar image urls
    email_md5 = db.StringProperty(default="")

    # email_verified is set after user clicked the link in verification mail
    email_verified = db.BooleanProperty(default=False)

    # The main reference to the Google-internal user object
    federated_identity = db.StringProperty()
    federated_provider = db.StringProperty()

    # Google user id is only used on the dev server
    google_user_id = db.StringProperty()

    # Various meta information
    date_joined = db.DateTimeProperty(auto_now_add=True)
    date_lastlogin = db.DateTimeProperty(auto_now_add=True)  # TODO
    date_lastactivity = db.DateTimeProperty(auto_now_add=True)  # TODO

    # is_setup: set to true after setting username and email at first login
    is_setup = db.BooleanProperty(default=False)

    # Cursom properties
    subscribed_to_newsletter = db.BooleanProperty(default=False)

    @staticmethod
    def from_user(user):
        """Returns the cached UserPrefs object. If not cached, get from DB and
        put it into memcache."""
        if not user:
            return None

        return mc.cache.get_userprefs(user)

    @staticmethod
    def _from_user(user):
        """Gets UserPrefs object from database. Used by
        mc.cache.get_userprefs() if not cached."""
        if user.federated_identity():
            # Standard OpenID user object
            q = db.GqlQuery("SELECT * FROM UserPrefs WHERE \
                federated_identity = :1", user.federated_identity())

        else:
            # On local devserver there is only the google user object
            q = db.GqlQuery("SELECT * FROM UserPrefs WHERE \
                google_user_id = :1", user.user_id())

        # Try to get the UserPrefs from the data store
        prefs = q.get()

        # If not existing, create now
        if not prefs:
            nick = user.nickname()
            if user.email():
                if not nick or "http://" in nick or "https://" in nick:
                    # If user has email and openid-url is nickname, replace
                    nick = user.email()

            # Create new user preference entity
            logging.info("Creating new UserPrefs for %s" % nick)
            prefs = UserPrefs(nickname=nick,
                    email=user.email(),
                    email_md5=md5(user.email().strip().lower()).hexdigest(),
                    federated_identity=user.federated_identity(),
                    federated_provider=user.federated_provider(),
                    google_user_id=user.user_id())

            # Save the newly created UserPrefs
            prefs.put()

        # Keep an internal reference to the Google user object (for
        # clearing the cache).
        prefs._user = user

        # Return either found or just created user preferences
        return prefs

    def put(self):
        """
        Overrides db.Model.put() to remove the cached object after an update.
        """
        # Call the put() method of the db.Model and keep the result
        key = super(UserPrefs, self).put()

        # Remove previously cached object. If put() is called the first time
        # (after creating the object) there would be no self._user.
        if hasattr(self, "_user"):
            self._clear_cache()

        # Return key provided by db.Model.put()
        return key

    def delete(self):
        """
        Overrides db.Model.delete() to remove the object from memcache.
        """
        super(UserPrefs, self).delete()
        self._clear_cache()

    def _clear_cache(self):
        """
        Removes the object from memcache. Automatically called on .put()
        and .delete().
        """
        mc.cache.get_userprefs(self._user, clear=True)


class YourCustomModel(db.Model):
    userprefs = db.ReferenceProperty(UserPrefs)

    demo_string_property = db.StringProperty()
    demo_boolean_property = db.BooleanProperty(default=True)
    demo_integer_property = db.IntegerProperty(default=1)
    demo_datetime_property = db.DateTimeProperty(auto_now_add=True)