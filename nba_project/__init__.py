from flask import Flask
from flask import render_template

import praw

import nba_py
from nba_py import game
#import pandas as pd

from datetime import datetime, timedelta

app = Flask(__name__)

#Reddit API
reddit = praw.Reddit(client_id="lwDHOduIraCz8g", 
					 client_secret="EKxjszUsqra8iT6gQzTn5YNmnrU", 
					 user_agent="NBA Stats - by Jayan Kamdar")

@app.route("/")
def index():
	"""Renders today's games on front page
	"""
	datetime_today = datetime.today()
	pretty_date_today = datetime_today.strftime("%b %d, %Y")

	games = get_games(datetime_today)

	return render_template("index.html", 
					title="Daily Scores",
					games=games,
					pretty_date_today=pretty_date_today)

def get_games(date):
	"""Get lists of games for the day

	Args:
		date: datetime object of the day that we want games

	Returns:
		games: array of dictionaries of games played today
	"""

	scoreboard = nba_py.Scoreboard(month=date.month, day=date.day, year=date.year)
	line_score = scoreboard.line_score()

	#uncomment below to check what line_score or score_header returns
	#print(line_score)
	#yesterday = date - timedelta(1)
	#print(nba_py.Scoreboard(month=yesterday.month, day=yesterday.day, year=yesterday.year).game_header())

	#List of games
	games = []
	#Dictionary of current game
	current_game = {}

	current_game_sequence = 0
	game_sequence_counter = 0

	for team in line_score:
		#Reached new game - fill in Team 1 information
		if (team["GAME_SEQUENCE"] != current_game_sequence):
			current_game["TEAM_1_ABBREVIATION"] = team["TEAM_ABBREVIATION"]
			current_game["TEAM_1_WINS_LOSSES"] = team["TEAM_WINS_LOSSES"]
			current_game["TEAM_1_CITY"] = team["TEAM_CITY_NAME"]

			current_game["TEAM_1_PTS"] = team["PTS"]
			current_game["TEAM_1_ID"] = team["TEAM_ID"]

			current_game_sequence = team["GAME_SEQUENCE"]
			game_sequence_counter += 1
		#Team 1 info exists, so now fill in Team 2 information
		elif (game_sequence_counter == 1):
			current_game["TEAM_2_ABBREVIATION"] = team["TEAM_ABBREVIATION"]
			current_game["TEAM_2_WINS_LOSSES"] = team["TEAM_WINS_LOSSES"]
			current_game["TEAM_2_CITY"] = team["TEAM_CITY_NAME"]

			current_game["TEAM_2_PTS"] = team["PTS"]
			current_game["TEAM_2_ID"] = team["TEAM_ID"]

			current_game["GAME_ID"] = team["GAME_ID"]

			current_game["GAME_STATUS"] = scoreboard.game_header()[current_game_sequence - 1]["LIVE_PERIOD"]
			current_game["GAME_STATUS_TEXT"] = scoreboard.game_header()[current_game_sequence -1]["GAME_STATUS_TEXT"]
			if (scoreboard.game_header()[current_game_sequence - 1]["GAME_STATUS_ID"] != 1):
				current_game["GAME_MARGIN"] = abs(current_game["TEAM_2_PTS"] - current_game["TEAM_1_PTS"])
			else:
				current_game["GAME_MARGIN"] = 0

			#Getting stream info
			current_game["GAME_STREAM"] = get_stream_thread(current_game["TEAM_2_CITY"], current_game["TEAM_1_CITY"])

			games.append(current_game)

			current_game = {}
			game_sequence_counter = 0

	return games

def get_stream_thread(home_team, away_team):
	subreddit = reddit.subreddit("nbastreams")
	query = away_team + " " + home_team

	for stream in subreddit.search(query, limit=1):
		if (stream):
			return (stream.url, stream.title)

	#return ("http://www.reddit.com/r/nbastreams/", "NBA Streams")
	return("https://www.reddit.com/r/nbastreams/search?q=" + home_team + "+" + away_team + "&restrict_sr=on&sort=relevance&t=all", "NBA Streams")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080, threaded=True, debug=True)