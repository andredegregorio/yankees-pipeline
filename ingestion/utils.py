import requests
import boto3
import json

BASE_URL = 'https://statsapi.mlb.com/api/v1'
BUCKET = 'yankees-pipeline-andre'
VALID_SPORT_IDS = (1, 11, 12, 13, 14) # MLB, AAA, AA, A+, A

def get_affiliate_team_ids(parent_org_id):
	try:
		response = requests.get(f'{BASE_URL}/teams/affiliates?teamIds={parent_org_id}')
		response.raise_for_status()
		teams = response.json().get('teams', [])
		filtered = [t for t in teams if t.get('sport', {}).get('id') in VALID_SPORT_IDS]
		for t in filtered:
			print(f"	{t['name']} (ID: {t['id']}, {t['sport']['name']})")
		return filtered
	except Exception as e:
		print(f"	Error fetching affiliates: {e}")
		return []
	

def upload_to_s3(data, path):
	print(f"	Uploading to {path}...")
	s3 = boto3.client('s3')
	s3.put_object(
		Bucket=BUCKET,
		Key=path,
		Body=json.dumps(data)
		)