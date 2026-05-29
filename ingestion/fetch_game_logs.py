import requests
from datetime import datetime
import argparse
from utils import get_affiliate_team_ids, upload_to_s3, BASE_URL
from fetch_roster import fetch_roster_data


def fetch_game_logs(team_id):
	'''
	Fetches game logs for all players on the roster of a given team and uploads to S3.
	Fetches both hitting and pitching logs based on player position.
	'''

	roster = fetch_roster_data(team_id)
	if not roster:
		print("Failed to fetch roster data.")
		return
	
	today = datetime.today().strftime('%Y-%m-%d')
	season = datetime.today().strftime('%Y')

	for player in roster.get("roster", []):
		player_id = player.get("person", {}).get("id")
		if not player_id:
			continue

		if player.get("position", {}).get("abbreviation") == "P":
			group = "pitching"
		else:
			group = "hitting"

		player_name = player.get("person", {}).get("fullName", "Unknown")
		print(f"  {player_name} ({group})...")

		try:
			response = requests.get(f"{BASE_URL}/people/{player_id}/stats?stats=gameLog&season={season}&group={group}")
			response.raise_for_status()
			data = response.json()
			path = f"raw/game_logs/{today}/player_{player_id}_{group}.json"
			upload_to_s3(data, path)
		except Exception as e:
			print(f"Error fetching game logs for player {player_id}: {e}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--org', type=int, default=147)
	args = parser.parse_args()
	
	print(f"Fetching player game logs for org {args.org}...")
	teams = get_affiliate_team_ids(args.org)

	for t in teams:
		fetch_game_logs(t['id'])

	print("\nDone.")