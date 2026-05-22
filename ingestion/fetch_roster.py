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
	
def upload_to_s3(data, team_id):
	s3 = boto3.client('s3')
	s3.put_object(
		Bucket='yankees-pipeline-andre',
		Key=f'raw/rosters/{datetime.now().strftime("%Y-%m-%d")}/team_{team_id}_roster.json',
		Body=json.dumps(data)
		)

if __name__ == '__main__':
    roster = fetch_roster_data(147)
    if roster:
        upload_to_s3(roster, 147)