import requests
from datetime import datetime
import argparse
from utils import get_affiliate_team_ids, upload_to_s3, BASE_URL

def fetch_roster_data(team_id):
	'''
	Fetches roster data for a given team ID and returns the JSON response.
	'''
	try:
		response = requests.get(f'{BASE_URL}/teams/{team_id}/roster')
		response.raise_for_status()
		data = response.json()
		player_count = len(data.get('roster', []))
		print(f'	Fetched {player_count} players')
		return data
	except Exception as e:
		print(f'	Error fetching roster: {e}')
		return None

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--org', type=int, default=147, help='Parent org team ID')
	args = parser.parse_args()

	print(f"Fetching affiliates for org {args.org}...")
	teams = get_affiliate_team_ids(args.org)
	today = datetime.today().strftime('%Y-%m-%d')

	for t in teams:
		print(f"\nFetching roster: {t['name']}...")
		roster = fetch_roster_data(t['id'])
		if roster:
			path = f"raw/rosters/{today}/team_{t['id']}_roster.json"
			upload_to_s3(roster, path)

	print("\nDone.")
