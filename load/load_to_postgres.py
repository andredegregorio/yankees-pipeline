import csv
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("SUPABASE_HOST"),
    port=os.getenv("SUPABASE_PORT"),
    dbname=os.getenv("SUPABASE_DB"),
    user=os.getenv("SUPABASE_USER"),
    password=os.getenv("SUPABASE_PASSWORD")
)

cur = conn.cursor()
with open('players.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cur.execute("""
            INSERT INTO players (mlb_id, first_name, last_name, birthdate, bats, throws, weight, position, draft_year, height_inches)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['mlb_id'], row['first_name'], row['last_name'],
            row['birthdate'], row['bats'], row['throws'],
            row['weight'] or None, row['position'],
            row['draft_year'] or None, row['height_inches'] or None
        ))

conn.commit()
cur.close()
conn.close()
print("Loaded players into Postgres")