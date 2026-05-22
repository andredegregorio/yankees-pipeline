import requests
import boto3
from datetime import datetime
import json

def fetch_roster_data(team_id):
	try:
		response = requests.get(f'https://statsapi.mlb.com/api/v1/teams/{team_id}/roster')
		response.raise_for_status()
		data = response.json()
		return data
	except Exception as e:
		print(f"Error fetching roster data: {e}")
		return None
	
def upload_to_s3(data, path):
	s3 = boto3.client('s3')
	s3.put_object(
		Bucket='yankees-pipeline-andre',
		Key=path,
		Body=json.dumps(data)
		)

if __name__ == '__main__':
	roster = fetch_roster_data(147)
	if roster:
		today = datetime.today().strftime('%Y-%m-%d')
		path = f'raw/rosters/{today}/team_147_roster.json'
		upload_to_s3(roster, path)