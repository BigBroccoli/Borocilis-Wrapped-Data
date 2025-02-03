import pandas as pd
import calendar
from datetime import datetime

def analyze_spotify_data(csv_path):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Debug
        print("\nAvailable columns in your CSV: ")
        print(df.columns.tolist())

        df['ts'] = pd.to_datetime(df['ts'])

        # Calcualte total time listened in hours
        total_time = df['ms_played'].sum() / (1000 * 60 * 60) # Convert ms to hrs

        required_columns = [
            'master_metadata_album_artist_name',
            'master_metadata_track_name',
            'master_metadata_album_album_name'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing columns: {missing_columns}")
            for col in missing_columns:
                print(f"- {col}")
            print("Please make sure the CSV file contains the required columns.")
            return False

        # Top 15 by listening time
        artists_by_time = df.groupby(['master_metadata_album_artist_name'])['ms_played'].sum().sort_values(ascending=False).head(15)
        songs_by_time = df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name'])['ms_played'].sum().sort_values(ascending=False).head(15)
        albums_by_time = df.groupby(['master_metadata_album_album_name', 'master_metadata_album_artist_name'])['ms_played'].sum().sort_values(ascending=False).head(15)

        # Top 15 by number of plays
        artists_by_plays = df.groupby(['master_metadata_album_artist_name']).size().sort_values(ascending=False).head(15)
        songs_by_plays = df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name']).size().sort_values(ascending=False).head(15)

        # Monthly top 15
        monthly_data = {}
        for month in range(1,13):
            month_df = df[df['ts'].dt.month == month]

            monthly_data[month] = {
                'artists': month_df.groupby(['master_metadata_album_artist_name'])['ms_played'].size().sort_values(ascending=False).head(15),
                'songs': month_df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name'])['ms_played'].size().sort_values(ascending=False).head(15)
            }

        # Print results
        print(f"\nTotal listening time: {total_time:.2f} hours\n")

        print("\nTop 15 artists by listening time in hours:")
        for artist, time in artists_by_time.items():
            print(f"{artist}: {time/3600000:.2f}")

        print("\nTop 15 songs by listening time in hours:")
        for (song, artist), time in songs_by_time.items():
            print(f"{song} by {artist}: {time/3600000:.2f}")

        print("\nTop 15 albums by listening time in hours:")
        for (album, artist), time in albums_by_time.items():
            print(f"{album} by {artist}: {time/3600000:.2f}")

        print("\nTop 15 artists by number of plays:")
        for artist, count in artists_by_plays.items():
            print(f"{artist}: {count}")

        print("\nTop 15 songs by number of plays:")
        for (song, artist), count in songs_by_plays.items():
            print(f"{song} by {artist}: {count}")

        print("\nMonthly top Artists and Songs: ")
        for month in range(1,13):
            if len(monthly_data[month]['artists']) > 0:
                print(f"\n{calendar.month_name[month]}")
                print("\nTop 15 artists by number of plays:")
                for artist, count in monthly_data[month]['artists'].items():
                    print(f"{artist}: {count}")

                print("\nTop 15 songs by number of plays:")
                for (song, artist), count in monthly_data[month]['songs'].items():
                    print(f"{song} by {artist}: {count}")

        return True
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return False