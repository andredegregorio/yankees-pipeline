from fetch_roster import fetch_roster_data, upload_to_s3
import requests
from datetime import datetime

BASE_URL = "https://statsapi.mlb.com/api/v1"

def fetch_game_logs(team_id):
	roster = fetch_roster_data(team_id)
	if not roster:
		print("Failed to fetch roster data.")
		return
	
	today = datetime.today().strftime('%Y-%m-%d')
	season = datetime.now().year

	for player in roster.get("roster", []):
		player_id = player.get("person", {}).get("id")
		if not player_id:
			continue

		if player.get("position", {}).get("abbreviation") == "P":
			group = "pitching"
		else:
			group = "hitting"
			
		try:
			response = requests.get(f"{BASE_URL}/people/{player_id}/stats?stats=gameLog&season={season}&group={group}")
			response.raise_for_status()
			data = response.json()
			path = f"raw/game_logs/{today}/player_{player_id}_{group}.json"
			upload_to_s3(data, path)
		except Exception as e:
			print(f"Error fetching game logs for player {player_id}: {e}")

if __name__ == "__main__":
	fetch_game_logs(147)  # Fetch game logs for the New York Yankees (team ID 147)