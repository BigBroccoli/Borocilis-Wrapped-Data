import os
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pylast
import time
from typing import List, Dict, Set
import logging

class GenreCaller:
    def __init__(self, spotify_client_id: str, spotify_client_secret: str, 
                 lastfm_api_key: str, lastfm_api_secret: str):
        # Initilize GenreCaller with Spotify and Last.fm credentials

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger - logging.getLogger(__name__)

        # Initialize Spotify client
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=spotify_client_id,
                client_secret=spotify_client_secret
            )
            self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            self.logger.error(f"Error initializing Spotify client: {e}")
            raise

        # Initialize Last.fm client
        try:
            self.lastfm = pylast.LastFMNetwork(
                api_key=lastfm_api_key,
                api_secret=lastfm_api_secret
            )
        except Exception as e:
            self.logger.error(f"Error initializing Last.fm client: {e}")
            raise

        # Rate limiting parameters
        self.spotify_delay = .25    # 250ms delay between Spotify API calls
        self.lastfm_delay = .25     # 250ms delay between Last.fm API calls

    def get_spotify_genres(self, artist_name: str, track_name: str) -> Set[str]:
        # Get genres from spotify for given artist and track
        try:
            time.sleep(self.spotify_delay)
            # Searh for track
            query = f"track:{track_name} artist:{artist_name}"
            results = self.spotify.search(q=query, type='track', limit=1)

            if not results['tracks']['items']:
                return set()
            
            # Get artist ID from the track
            artist_id = results['tracks']['items'][0]['artists'][0]['id']

            # Get artist genres
            time.sleep(self.spotify_delay)
            artist = self.spotify.artist(artist_id)
            return set(artist['genres'])
        
        except Exception as e:
            self.logger.error(f"Error getting Spotify genres for {artist_name} - {track_name}: {e}")
            return set()
        
    def get_lastfm_genres(self, artist_name: str, track_name: str) -> Set[str]:
        # Get genres from Last.fm for given artist and track
        try:
            time.sleep(self.lastfm_delay)
            artist = self.lastfm.get_artist(artist_name)
            tags = artist.get_top_tags(limit=10)
            return {tag.item.get_name() for tag in tags}
        
        except Exception as e:
            self.logger.error(f"Error getting Last.fm genres for {artist_name} - {track_name}: {e}")
            return set()
        
    def process_songs(self, csv_path: str, output_path: str = None) -> pd.DataFrame:
        # Process songs in the CSV file and add genre information

        try:
            # read CSV file
            df = pd.read_csv(csv_path)

            # Add columns for genres if doesn't exist
            if 'genres' not in df.columns:
                df['genres'] = None

            for idx, row in df.iterrows():
                artist_name = row['artist']
                track_name = row['track']

                self.logger.info(f"Processing song: {artist_name} - {track_name}")

                # Skip if genres already exist
                if pd.notna(row.get('genres')):
                    continue
                
                # Get genres from Spotify and Last.fm
                spotify_genres = self.get_spotify_genres(artist_name, track_name)
                lastfm_genres = self.get_lastfm_genres(artist_name, track_name)

                # Combine genres
                combined_genres = spotify_genres.union(lastfm_genres)

                # Store as comma-separated string
                df.at[idx, 'genres'] = ', '.join(combined_genres) if combined_genres else ''

                if idx % 10 == 0:
                    self.logger.info(f"Processed {idx} songs.")
                    # Save progress
                    df.to_csv(csv_path, index=False)

            # Save final result
            df.to_csv(csv_path, index=False)
            self.logger.info(f"Completed processing, results save to {csv_path}")

            return df
        
        except Exception as e:
            self.logger.error(f"Error processing songs: {e}")
            return