"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.api import taskqueue


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    points_earned = ndb.IntegerProperty(default=0)

    def to_ranking(self):
        form = RankingForm()
        form.name = self.name
        form.points_earned = self.points_earned
        return form


class RankingForm(messages.Message):
    """Ranking form"""
    name = messages.StringField(1, required=True)
    points_earned = messages.IntegerField(2, required=True)


class Rankings(messages.Message):
    """Return multiple Leaders."""
    rankings = messages.MessageField(RankingForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class GameData(ndb.Model):
    """Data used for game play."""
    sayer_category = ndb.StringProperty(required=True)
    sayer = ndb.StringProperty(required=True)
    saying = ndb.StringProperty(required=True)
    hints = ndb.StringProperty(required=True)

    @classmethod
    def new_game_data(cls, sayer_category, sayer, saying, hints):
        game_data = GameData(sayer_category=sayer_category,
                             sayer=sayer,
                             saying=saying,
                             hints=hints)
        game_data.put()
        return game_data


class NewGameDataForm(messages.Message):
    """Used to create new game data."""
    sayer_category = messages.StringField(1, required=True)
    sayer = messages.StringField(2, required=True)
    saying = messages.StringField(3, required=True)
    hints = messages.StringField(4, required=True)


class SayerCategory(messages.Enum):
        ACTOR = 1
        SINGER = 2
        AUTHOR = 3
        ENTREPRENEUR = 4


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    sayer_category = messages.EnumField(SayerCategory, 2,
                                        required=True,
                                        default='ACTOR')
    num_hints = messages.IntegerField(3, required=True, default=0)


class Game(ndb.Model):
    """Game object"""
    who_says = ndb.StringProperty(required=True)
    saying = ndb.StringProperty(required=True)
    sayer_category = ndb.StringProperty(required=True)
    status = ndb.StringProperty(required=True, default='NEW')
    user = ndb.KeyProperty(required=True, kind='User')
    num_hints = ndb.IntegerProperty(required=True)
    hints = ndb.StringProperty(repeated=True)
    points = ndb.IntegerProperty(required=True, default=85)

    @classmethod
    def new_game(cls, user, sayer_category, num_hints):
        """Creates and returns a new game"""
        if num_hints < 0 or num_hints > 5:
            raise ValueError('Number of hints must be between 0 and 5')
        num_points = 85
        if num_hints == 1:
            num_points = 80
        elif num_hints == 2:
            num_points = 72
        elif num_hints == 3:
            num_points = 59
        elif num_hints == 4:
            num_points = 38
        elif num_hints == 5:
            num_points = 4
        else:
            num_points = 85

        game_data = GameData.query(
            GameData.sayer_category == sayer_category.name).get()

        if not game_data:
            raise ValueError('sayer_category not found.')
        else:
            sayer = game_data.sayer
            saying = game_data.saying

            # parse hints into list and assign to game.hints
            hintsStr = game_data.hints
            hints = hintsStr.split('^^')
            hintSentences = [
                "The year it was said: %s.",
                "The genre or industry in which it was said: %s.",
                "The sayer's gender: %s.",
                "The medium in which it was said: %s.",
                "The sayer's initials: %s."
            ]
            userHints = []
            for x in range(num_hints):
                userHints.append(hintSentences[x] % hints[x])
        game = Game(user=user,
                    sayer_category=sayer_category.name,
                    who_says=sayer,
                    saying=saying,
                    points=num_points,
                    num_hints=num_hints,
                    hints=userHints)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.status = self.status
        form.saying = self.saying
        form.hints = ' '.join(self.hints)
        form.points_possible = self.points
        form.message = message
        return form

    def to_score_report(self):
        form = ScoreReport()
        form.user_name = self.user.get().name
        form.status = self.status
        form.points = self.points
        return form

    def to_game_analysis(self):
        form = GameAnalysis()
        user = self.user.get()
        form.user_name = user.name
        form.sayer_category = self.sayer_category
        form.hints_purchased = self.num_hints
        form.game_status = self.status
        return form

    @ndb.transactional(xg=True)
    def do_move(self):
        self.status = 'WON'
        self.put()

        user = self.user.get()
        user.points_earned += self.points
        user.put()

        taskqueue.add(url='/tasks/cache_average_game_points')


class GameAnalysis(messages.Message):
    """GameAnalysis for outbound analysis."""
    user_name = messages.StringField(1, required=True)
    sayer_category = messages.StringField(2, required=True)
    hints_purchased = messages.IntegerField(3, required=True)
    game_status = messages.StringField(4, required=True)


class Analysis(messages.Message):
    """Return game analysis."""
    analysis = messages.MessageField(GameAnalysis, 1, repeated=True)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    saying = messages.StringField(2, required=True)
    hints = messages.StringField(3, required=True)
    status = messages.StringField(4, required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)
    points_possible = messages.IntegerField(7, required=True)


class MakeMoveForm(messages.Message):
    """Used to take a guess in an existing game."""
    guess = messages.StringField(1, required=True)


class ScoreReport(messages.Message):
    """ScoreReport for outbound Score information."""
    user_name = messages.StringField(1, required=True)
    status = messages.StringField(2, required=True)
    points = messages.IntegerField(3, required=True)


class GameHighScores(messages.Message):
    """Return multiple ScoreReports."""
    high_scores = messages.MessageField(ScoreReport, 1, repeated=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms."""
    scores = messages.MessageField(ScoreReport, 1, repeated=True)


class GameForms(messages.Message):
    """Return multiple GameForms."""
    games = messages.MessageField(GameForm, 1, repeated=True)
