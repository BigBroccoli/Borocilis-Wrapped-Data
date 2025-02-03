import pandas as pd
import glob
import os
from datetime import datetime

def process_json_files(json_path_pattern, chunksize=50000):
    # Create directory for output
    output_dir = 'spotify_data_by_year'
    os.makedirs(output_dir, exist_ok=True) 

    # Define columns to keep
    columns_to_keep = [
        'ts',
        'platform',
        'ms_played',
        'conn_country',
        'master_metadata_track_name',
        'master_metadata_album_artist_name',
        'master_metadata_album_album_name',
        'spotify_track_uri',
        'reason_start',
        'reason_end',
        'shuffle',
        'skipped',
        'offline',
        'offline_timestamp'
    ]

    def save_chunk_by_year(df):
        # Convert timestamp to datetime
        df['ts'] = pd.to_datetime(df['ts'])

        # Keep only wanted columns
        df = df[columns_to_keep]

        # Sort by timestamp
        df = df.sort_values('ts')

        # Group by year and save to CSV
        for year, year_data in df.groupby(df['ts'].dt.year):
            file_path = os.path.join(output_dir, f"spotify_data_{year}.csv")
            header = not os.path.exists(file_path)
            year_data.to_csv(file_path, mode='a', header=header, index=False)

    try:
        for json_file in glob.glob(json_path_pattern):
            print(f"Processing file: {json_file}")
            try:
                df = pd.read_json(json_file)
                save_chunk_by_year(df)
                print(f"Successfully processed {json_file}")
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                continue

        print("Finished processing all files")

        for file in glob.glob(os.path.join(output_dir, "spotify_data_*.csv")):
            try:
                df = pd.read_csv(file)
                df['ts'] = pd.to_datetime(df['ts'])
                df = df.sort_values('ts')
                df.to_csv(file, index=False)
            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue

    except Exception as e:
        print(f"Error processing files: {e}")
        