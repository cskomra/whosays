# "Who Says?" Game API

## "Who Says?" Game Description:
"Who says?" is a simple guessing game where the object of the game is to guess who said the 'saying'.
Each game begins with a 'saying' based on the player's choice of one of the following categories of 'Sayers': ACTOR, SINGER, AUTHOR, or ENTREPRENEUR.
A Player starts with 85 points and may purchase up to five 'hints' prior to starting the game. Hints are purchased prior to seeing the Saying.
If the correct guess is received by the 'make_move' endpoint, it will reply with 'You win!' otherwise, it will reply with 'You lose.'

You are given a 'Saying'. You need to guess who said it.

Hints are priced as follows:

 - 1 Hint for 5 points gets you the year the saying was said.
 - 2 Hints for 13 points adds the genre or industry in which the saying was said.
 - 3 Hints for 26 points adds the sayer's gender.
 - 4 hints for 47 points adds the movie/song/book/industry in which it was said.
 - 5 hints for 81 points adds the sayer's initials.

Each player gets one guess per game, which when sent to the 'make_move' endpoint will reply with either 'You lose.' or 'You win!' If you win, your game points are added to your user entity's accumulating score.

Game points are calculated as follows:
- Every game offers 85 points with which a player may purchase one or more hints.
- If hints are purchased, the cost of the hints is deducted from the offered points (85).
- If the player wins, points are added to the player's earned_points value on his/her user profile.
- If the player loses, points are forfitted, but are recorded in the game entity for future game community analysis.

High scores are measured based on a game instance. The highest score possible is one in which no hints were purchased for that game: 85 points.

User rankings are based on the user's accumulated earned_points in his/her profile.

Use `get_high_scores` and `get_user_rankings` endpoints to check player standings in the game community.

Many different 'Who Says?' games can be played by many different Users at any given time. Each game can be retrieved or played by using the path parameter `urlsafe_game_key`.


## Files Included:
 - [whosays_api.py](whosays_api.py): Contains endpoints and game playing logic.
 - [app.yaml](app.yaml): App configuration.
 - [cron.yaml](cron.yaml): Cronjob configuration.
 - [main.py](main.py): Handler for taskqueue and cronjob handlers.
 - [models.py](models.py): Entity and message definitions including helper methods.
 - [utils.py](utils.py): Helper function for retrieving ndb.Models by urlsafe Key string.

## Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **add_data**
    - Path: 'adddata'
    - Method: POST
    - Parameters: sayer, sayer_category, saying, hints
    - Returns: Message confirming creation of game data.
    - Description: Creates game data for game use. (This is currently an administrative endpoint to be replaced later by well-formed, more user-friendly data structures and functionality. It is here now to facilitate adding data with which to play the game. In later versions, users might add their own game data and possibly earn bonus points for doing so.)

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, sayer_category, num_hints
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. num_hints must be between 0 and 5. sayer_category must be one of the following: ACTOR, SINGER, AUTHOR, ENTREPRENEUR.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game. Also adds a task to a task queue to update the average game points earned.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_average_game_points**
    - Path: 'games/averagepoints'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average game points won since the beginning of time.

 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name, email (optional)
    - Returns: List of GameForms
    - Description: Returns all of a user's active (NEW) games.

 - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: StringMessage confirming cancellation
    - Description: Cancells a game by setting game status to CANCELLED.

 - **get_high_scores**
    - Path: 'games/highscores'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: list of ScoreReport forms in descending order
    - Description: Returns a list of high scores in descending order.

 - **get_user_rankings**
    - Path: 'users/rankings'
    - Method: GET
    - Parameters: None
    - Returns: list of user Rankings
    - Description: Returns a list of all players ranked by total points_earned.

 - **get_game_analysis**
    - Path: 'games/analysis'
    - Method: GET
    - Parameters: None
    - Returns: list of GameAnalysis forms
    - Description: Returns category and hints_purchased choices along with game results to give an idea of how well players are doing in light of the choices they make.
    (Note: This takes the place of get_game_history which didn't make as much sense given this game's design.)


## Models Included:
 - **User**
    - Stores unique user_name (optional) email address and earned_points.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **GameData**
    - Stores data used for playing the game.

## Forms Included:
- **RankingForm**
    - Represents a user ranking (name, points_earned)
- **Rankings**
    - Multiple RankingForm container.
- **GameForm**
    - Representation of a Game's state (urlsafe_key, saying, hints, status, message, user_name, points_possible).
- **NewGameForm**
    - Used to create a new game (user_name, sayer_category, num_hints)
- **MakeMoveForm**
    - Inbound make move form used to take a guess in an existing game (guess).
- **ScoreReport**
    - Representation of a completed game's Score (user_name, status, points).
- **ScoreForms**
    - Multiple ScoreReport container.
- **StringMessage**
    - General purpose String container.
- **NewGameDataForm**
    - Used to create new game data (sayer_category, sayer, saying, hints)
- **GameAnalysis**
    - Outbound. For analysis of game information (user_name, sayer_category, hints_purchased, game_status)
- **ScoreReport**
    - Outbound. To report score information (user_name, status, points)
- **GameHighScores**
    - Outbound. Returns multiple ScoreReports.
- **GameForms**
    - Outbound. Returns multiple GameForms.

## Set-Up Instructions:
### Set Up Environment
1. Update the value of application in `app.yaml` to the app ID you have registered in the App Engine admin console and would like to use to host your instance of this sample.
2. Using App Engine Launcher, add an existing application; and point it to the application's directory.
3. Select the application in App Engine Launcher and click `Run`.  (Note the port and admin port numbers)
4. In your browser, use the port number you just noted to go to:
 `localhost:<your_port_number>/_ah/api/explorer`
5. Click on `whosaysendpoints API` to reveal the list of available endpoints

### Set Up Data (Required)
Set up Game Data prior to playing.
In Version 1 of 'Who Says?' this is done with the `add_data` endpoint. Future versions will have a more traditional data model. Until then, create 4 GameData sample entities to get you started. (Note: hints are marked as code for clarity. Input exactly as is, or copy/paste.)

1. Add the following with the `add_data` endpoint:
    - hints:            `1987^^Fantasy^^Male^^Princess Bride^^BC`
    - sayer:            Billy Crystal
    - sayer_category:   ACTOR
    - saying:           You ARE the brute squad!

2. Add the following with the `add_data` endpoint:
    - hints:            `1969^^Pop Rock^^Male^^Space Oddity^^DB`
    - sayer:            David Bowie
    - sayer_category:   SINGER
    - saying:           Ground control to Major Tom

3. Add the following with the `add_data` endpoint:
    - hints:            `1997^^Fantasy^^Female^^Harry Potter and the Philosopher's Stone^^JKR`
    - sayer:            J.K. Rowling
    - sayer_category:   AUTHOR
    - saying:           It does not do to dwell on dreams and forget to live.

4. Add the following with the `add_data` endpoint:
    - hints:            `2014^^Tech^^Male^^Zero to One^^PT`
    - sayer:            Peter Thiel
    - sayer_category    ENTREPRENEUR
    - saying:           A great company is a conspiracy to change the world.


### To begin playing

1. Use create_user endpoint to create one or more users/players.
2. Use new_game to start a new game.
3. Use make_move to take a guess.
