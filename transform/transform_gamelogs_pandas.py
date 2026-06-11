import argparse, io, json
import boto3
import pandas as pd
import logging


logger = logging.getLogger(__name__)

BUCKET = "yankees-pipeline-andre"
RAW_PREFIX = "raw/game_logs"
OUT_PREFIX = "transformed/parquet/game_logs"

s3 = boto3.client("s3")

HITTING_COLS = [
    # identity / keys
    'player.id', 'player.fullName', 'game.gamePk', 'date', 'season',
    # dimensions
    'sport.id', 'sport.abbreviation', 'league.id', 'league.name',
    'team.id', 'team.name', 'opponent.id', 'opponent.name',
    'gameType', 'isHome', 'game.dayNight', 'positionsPlayed',
    # stats
    'stat.runs', 'stat.hits', 'stat.doubles', 'stat.triples', 'stat.homeRuns',
    'stat.rbi', 'stat.totalBases', 'stat.baseOnBalls', 'stat.intentionalWalks',
    'stat.strikeOuts', 'stat.hitByPitch', 'stat.atBats', 'stat.plateAppearances',
    'stat.stolenBases', 'stat.caughtStealing', 'stat.groundIntoDoublePlay',
    'stat.numberOfPitches', 'stat.leftOnBase', 'stat.sacBunts', 'stat.sacFlies',
]

HITTING_MAP ={
    'player.id': 'player_id',
    'player.fullName': 'player_name',
    'game.gamePk': 'game_pk',
    'date': 'game_date',
    'sport.id': 'sport_id',
    'sport.abbreviation': 'level',
    'league.id': 'league_id',
    'league.name': 'league_name',
    'team.id': 'team_id',
    'team.name': 'team_name',
    'opponent.id': 'opponent_id',
    'opponent.name': 'opponent_name',
    'gameType': 'game_type',
    'isHome': 'is_home',
    'game.dayNight': 'day_night',
    'positionsPlayed': 'positions_played',
    'stat.runs': 'r',
    'stat.hits': 'h',
    'stat.doubles': 'x2b',
    'stat.triples': 'x3b',
    'stat.homeRuns': 'hr',
    'stat.rbi': 'rbi',
    'stat.totalBases': 'tb',
    'stat.baseOnBalls': 'bb',
    'stat.intentionalWalks': 'ibb',
    'stat.strikeOuts': 'so',
    'stat.hitByPitch': 'hbp',
    'stat.atBats': 'ab',
    'stat.plateAppearances': 'pa',
    'stat.stolenBases': 'sb',
    'stat.caughtStealing': 'cs',
    'stat.groundIntoDoublePlay': 'gidp',
    'stat.numberOfPitches': 'np',
    'stat.leftOnBase': 'lob',
    'stat.sacBunts': 'sh',
    'stat.sacFlies': 'sf',
}

PITCHING_COLS =  [
    # identity / keys
    'player.id', 'player.fullName', 'game.gamePk', 'date', 'season',
    # dimensions
    'sport.id', 'sport.abbreviation', 'league.id', 'league.name',
    'team.id', 'team.name', 'opponent.id', 'opponent.name',
    'gameType', 'isHome', 'game.dayNight',
    # stats
    'stat.gamesStarted', 'stat.runs', 'stat.doubles',
    'stat.triples', 'stat.homeRuns', 'stat.strikeOuts', 'stat.baseOnBalls',
    'stat.intentionalWalks', 'stat.hits', 'stat.atBats',
    'stat.caughtStealing', 'stat.stolenBases', 'stat.groundIntoDoublePlay',
    'stat.numberOfPitches', 'stat.wins', 
    'stat.losses', 'stat.saves', 'stat.saveOpportunities', 'stat.holds',
    'stat.blownSaves', 'stat.earnedRuns', 'stat.battersFaced',
    'stat.outs', 'stat.completeGames', 'stat.shutouts',
    'stat.strikes', 'stat.hitBatsmen',
    'stat.balks', 'stat.wildPitches', 'stat.pickoffs', 'stat.totalBases', 
    'stat.gamesFinished', 'stat.inheritedRunners',
    'stat.inheritedRunnersScored',
    'stat.sacBunts', 'stat.sacFlies',
    ]

PITCHING_MAP = {
    'player.id': 'player_id',
    'player.fullName': 'player_name',
    'game.gamePk': 'game_pk',
    'date': 'game_date',
    'sport.id': 'sport_id',
    'sport.abbreviation': 'level',
    'league.id': 'league_id',
    'league.name': 'league_name',
    'team.id': 'team_id',
    'team.name': 'team_name',
    'opponent.id': 'opponent_id',
    'opponent.name': 'opponent_name',
    'gameType': 'game_type',
    'isHome': 'is_home',
    'game.dayNight': 'day_night',
    'stat.gamesStarted': 'gs',
    'stat.runs': 'r',
    'stat.doubles': 'x2b',
    'stat.triples': 'x3b',
    'stat.homeRuns': 'hr',
    'stat.strikeOuts': 'so',
    'stat.baseOnBalls': 'bb',
    'stat.intentionalWalks': 'ibb',
    'stat.hits': 'h',
    'stat.atBats': 'ab',
    'stat.caughtStealing': 'cs',
    'stat.stolenBases': 'sb',
    'stat.groundIntoDoublePlay': 'gidp',
    'stat.numberOfPitches': 'np',
    'stat.wins': 'w',
    'stat.losses': 'l',
    'stat.saves': 'sv',
    'stat.saveOpportunities': 'svo',
    'stat.holds': 'hld',
    'stat.blownSaves': 'bs',
    'stat.earnedRuns': 'er',
    'stat.battersFaced': 'bf',
    'stat.outs': 'outs',
    'stat.completeGames': 'cg',
    'stat.shutouts': 'sho',
    'stat.strikes': 'strikes',
    'stat.hitBatsmen': 'hbp',
    'stat.balks': 'balks',
    'stat.wildPitches': 'wp',
    'stat.pickoffs': 'pickoffs',
    'stat.totalBases': 'tb',
    'stat.gamesFinished': 'gf',
    'stat.inheritedRunners': 'ir',
    'stat.inheritedRunnersScored': 'irs',
    'stat.sacBunts': 'sh',
    'stat.sacFlies': 'sf',
}

def transform_hitters(df):
    '''
    Hitter-specific transformations go here.
    '''
    df['positions_played'] = df['positions_played'].apply(lambda x: ','.join(p['abbreviation'] 
                            for p in x) if isinstance(x, list) else '')
    return df

def latest_date(prefix=RAW_PREFIX + "/"):
    '''Newest date= folder directly under game_logs/.'''
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix, Delimiter="/")
    dates = [p["Prefix"].rstrip("/").split("/")[-1]
             for p in resp.get("CommonPrefixes", [])]
    return max(dates)  # ISO strings sort correctly

def process_group(group, cols, mapping, transform_fn, date):
    '''
    Process one group (hitting/pitching) for one date.

    Lists the raw JSON files in S3 under that group/date, reads and stacks them
    into one DataFrame (all players, all levels), cleans it (reindex to `cols`,
    rename via `mapping`, cast game_date/season), runs `transform_fn` if given,
    and writes the result to S3 as Parquet.

    Args:
        group:        "hitting" or "pitching" — builds the S3 prefixes.
        cols:         column list to keep/reorder (HITTING_COLS or PITCHING_COLS).
        mapping:      rename dict (HITTING_MAP or PITCHING_MAP).
        transform_fn: optional group-specific step, or None.
        date:         partition to process (YYYY-MM-DD).
    '''
    # extract
    prefix = f"{RAW_PREFIX}/{date}/"
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    keys = [o["Key"] for o in resp.get("Contents", [])
            if o["Key"].endswith(f"_{group}.json")]
    if not keys:
        logger.warning("no %s files under %s, skipping", group, prefix)
        return
 
    dfs = []
    for key in keys:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        df = pd.json_normalize(json.loads(obj["Body"].read()))
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
 
    # transform
    missing = set(cols) - set(df.columns)
    if missing:
        logger.warning('reindex filling missing columns with NaN: %s', missing)
    df = df.reindex(columns=cols).copy()
    df = df.rename(columns=mapping)
    df['game_date'] = pd.to_datetime(df['game_date'], format='%Y-%m-%d')
    df['season'] = df['season'].astype('Int64')
 
    if transform_fn:
        df = transform_fn(df)
 
    # load
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    out_key = f"{OUT_PREFIX}/{group}/date={date}/data.parquet"
    s3.put_object(Bucket=BUCKET, Key=out_key, Body=buf.getvalue())
    logger.info("Processed %d rows for %s on %s, output to %s", len(df), group, date, out_key)

def main(date=None):
    logging.basicConfig(level=logging.INFO)
    if date is None:
        date = latest_date(f"{RAW_PREFIX}/hitting/")
    logger.info("processing date=%s", date)
    process_group("hitting", HITTING_COLS, HITTING_MAP, transform_hitters, date)
    process_group("pitching", PITCHING_COLS, PITCHING_MAP, None, date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD; defaults to latest in S3")
    args = parser.parse_args()
    main(args.date)
