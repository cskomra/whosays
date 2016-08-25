#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from whosays_api import WhoSaysApi

from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        games = Game.query(Game.status == 'NEW')
        sendList = []
        for game in games:
            user = game.user.get()
            if user not in sendList and user.email:
                subject = "'Who Says' game reminder!"
                body = "Hello {}, you have one or more unfinished 'Who Says' games!".format(user.name)
                # This will send test emails, the arguments to send_mail are: from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)
            sendList.append(user)


class UpdateAverageGamePoints(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        WhoSaysApi._cache_average_game_points()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_game_points', UpdateAverageGamePoints),
], debug=True)