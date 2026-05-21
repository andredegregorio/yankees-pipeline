import requests
import boto3
from datetime import datetime
import json

def fetch_roster_data(team_id):
	data = requests.get(f'https://statsapi.mlb.com/api/v1/teams/{team_id}/roster').json()
	s3 = boto3.client('s3')
	s3.put_object(
		Bucket='yankees-pipeline-andre',
		Key=f'raw/rosters/{datetime.now().strftime("%Y-%m-%d")}/team_{team_id}_roster.json',
		Body=json.dumps(data)
		)
	
if __name__ == '__main__':
    fetch_roster_data(147)