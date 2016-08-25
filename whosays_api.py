"""Hello World API implemented using Google Cloud Endpoints.

Contains declarations of endpoint, endpoint methods,
as well as the ProtoRPC message class and container required
for endpoint method definition.
"""
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache

from models import User, StringMessage, NewGameDataForm
from models import GameData, NewGameForm, GameForm, GameForms
from models import Game, MakeMoveForm, ScoreReport, ScoreForms
from models import RankingForm, Rankings, GameHighScores
from models import GameAnalysis, Analysis
from utils import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2))
ADD_DATA = endpoints.ResourceContainer(NewGameDataForm)
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1))
MEMCACHE_AVE_PTS_PER_GAME = 'AVE_PTS_PER_GAME'
HIGH_SCORE_REQUEST = endpoints.ResourceContainer(
  number_of_results=messages.IntegerField(1))

package = 'WhoSays'


@endpoints.api(name='whosaysendpoints', version='v1')
class WhoSaysApi(remote.Service):
    """WhoSaysAPI v1."""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))


    @endpoints.method(request_message=ADD_DATA,
                      response_message=StringMessage,
                      path='adddata',
                      name='add_data',
                      http_method='POST')
    def add_data(self, request):
        """Add game data. Administrative."""
        gData = GameData.new_game_data(sayer_category=request.sayer_category,
                                       sayer=request.sayer,
                                       saying=request.saying,
                                       hints=request.hints)
        gData.put()
        return StringMessage(message='Successfully added {}.'.format(request.saying))


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Start a new game."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key,
                                 request.sayer_category,
                                 request.num_hints)
        except ValueError:
            raise endpoints.BadRequestException('Number of hints must be between 0 and 5')
        return game.to_form("Good luck playing Who Says!")


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to take a guess!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Make a move and return a game state with message."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.status != 'NEW':
            return game.to_form('Game already over!')

        if request.guess == game.who_says:
            game.do_move()
            return game.to_form('You win!')

        else:
            game.status = 'LOST'
            game.put()
            return game.to_form('You lost.')


    @endpoints.method(response_message=ScoreForms,
                     path='scores',
                     name='get_scores',
                     http_method='GET')
    def get_scores(self, request):
        """Return all Game scores."""
        qResults = Game.query(Game.status == 'WON')
        if not qResults:
            raise endpoints.NotFoundException('Scores not found.')
        return ScoreForms(scores=[game.to_score_report() for game in qResults])


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Return all of an individual User's game scores."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        qResults = Game.query(Game.user == user.key)
        return ScoreForms(scores=[game.to_score_report() for game in qResults])


    @endpoints.method(response_message=StringMessage,
                      path='games/averagepoints',
                      name='get_average_game_points',
                      http_method='GET')
    def get_average_game_points(self, request):
        """Return average game points."""
        avePoints = memcache.get(MEMCACHE_AVE_PTS_PER_GAME)
        if not avePoints:
            avePoints = 'Average points are not available.'
        return StringMessage(message=avePoints)


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all of an individual User's games."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        qResults = Game.query(Game.user == user.key, Game.status == 'NEW')
        if not qResults:
            raise endpoints.NotFoundException(
                'There are no user games in progress.')

        return GameForms(games=[game.to_form('Game in progress.') for game in qResults])


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Set the game status to cancelled."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.status != 'NEW':
                return StringMessage(message='Game already over or cancelled.')
            game.status = 'CANCELLED'
            game.put()
            return StringMessage(message='Game cancelled!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=HIGH_SCORE_REQUEST,
                      response_message=GameHighScores,
                      path='games/highscores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
      """Return game high scores in descending order."""
      if request.number_of_results:
        highScores = Game.query(Game.status == 'WON').order(-Game.points).fetch(request.number_of_results)
      else:
        highScores = Game.query(Game.status == 'WON').order(-Game.points)
      if not highScores:
          raise NotFoundException('Scores not found.')
      return GameHighScores(high_scores=[game.to_score_report() for game in highScores])


    @endpoints.method(response_message=Rankings,
                      path='users/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return top all users' high scores in descending order."""
        userRankings = User.query(User.points_earned > 0).order(-User.points_earned)
        if not userRankings:
            raise NotFoundException('Rankings not found.')
        return Rankings(rankings=[user.to_ranking() for user in userRankings])


    @endpoints.method(response_message=Analysis,
                      path='games/analysis',
                      name='get_game_analysis',
                      http_method='GET')
    def get_game_analysis(self, request):
      """Return history of in-game choices."""
      games = Game.query().order(Game.user)
      if not games:
        raise NotFoundException('Games not found.')
      return Analysis(analysis=[game.to_game_analysis() for game in games])


    @staticmethod
    def _cache_average_game_points():
        """Populates memcache with average points won per game."""
        games = Game.query(Game.status == 'WON').fetch()
        if games:
            count = len(games)
            total_points = sum([game.points for game in games])
            average = float(total_points)/count
            memcache.set(MEMCACHE_AVE_PTS_PER_GAME,
                         'Average points won per game is {:.2f}'.format(average))


APPLICATION = endpoints.api_server([WhoSaysApi])
