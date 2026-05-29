import requests
from datetime import datetime
import argparse
from utils import get_affiliate_team_ids, upload_to_s3, BASE_URL
from fetch_roster import fetch_roster_data


def fetch_player_info(team_id): 
	'''
	Fetches player info for all players on the roster of a given team and uploads to S3.
	'''

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
			print(f"  Fetching player info for player ID: {player_id}...")
			response = requests.get(f"{BASE_URL}/people/{player_id}")
			response.raise_for_status()
			data = response.json()
			path = f"raw/player_info/{today}/player_{player_id}.json"
			upload_to_s3(data, path)
		except Exception as e:
			print(f"Error fetching player info for player {player_id}: {e}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--org', type=int, default=147)
	args = parser.parse_args()

	print(f"Fetching player info for org {args.org}...")
	teams = get_affiliate_team_ids(args.org)

	for t in teams:
		fetch_player_info(t['id'])

	print("\nDone.")