from fetch_roster import fetch_roster_data, get_affiliate_team_ids, upload_to_s3
import requests
from datetime import datetime
import argparse


BASE_URL = "https://statsapi.mlb.com/api/v1"

def fetch_player_info(team_id):
	teams = get_affiliate_team_ids(parent_team_id)

	roster = fetch_roster_data(team_id)
	if not roster:
		print("Failed to fetch roster data.")
		return
	
	today = datetime.today().strftime('%Y-%m-%d')

	for player in roster.get("roster", []):
		player_id = player.get("person", {}).get("id")
		if not player_id:
			continue
			
		try:
			response = requests.get(f"{BASE_URL}/people/{player_id}")
			response.raise_for_status()
			data = response.json()
			path = f"raw/player_info/{today}/player_{player_id}.json"
			upload_to_s3(data, path)
		except Exception as e:
			print(f"Error fetching player info for player {player_id}: {e}")

if __name__ == "__main__":
	fetch_player_info(147)  # Fetch player info for the New York Yankees (team ID 147)