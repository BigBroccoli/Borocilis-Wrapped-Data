import sys
import os
import Preprocessor as pp
import BasicAnalysis as ba
from GenreCaller import GenreCaller

def get_user_input(prompt):
    while True:
        response = input(prompt).lower()
        if response in ['y', 'n']:
            return response == 'y'
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")
    
if __name__ == '__main__':
    # Ask user if they want to preprocess the new data
    process_new = get_user_input("Do you want to process new JSON data? (y/n): ")

    if process_new:
        if len(sys.argv) < 2:
            print("Please provide the path to the JSON files.")
            sys.exit(1)
        
        json_path_pattern = sys.argv[1]
        print(f"Processing JSON files at: {json_path_pattern}")
        pp.process_json_files(json_path_pattern)

    while True:
        try:
            year = input("Enter the year you want to analyze (e.g., 2023) or 'q' to quit: ")

            if year.lower() == 'q':
                print("Quitting...")
                break

            try:
                if not year.isdigit():
                    not_digit = "Please enter a valid year or 'q' to quit."

                csv_path = os.path.join('spotify_data_by_year', f"spotify_data_{year}.csv")

            except ValueError:
                print(not_digit)
                continue

            if not os.path.exists(csv_path):
                print(f"No data found for {year}.")
                continue

            print(f"Analyzing data for {year}...")
            ba.analyze_spotify_data(csv_path)  

            if get_user_input("Do you want to fetch genres? (y/n): "):
                try:
                    spotify_client_id = os.environ('SPOTIFY_CLIENT_ID')
                    spotify_client_secret = os.environ('SPOTIFY_CLIENT_SECRET')
                    lastfm_api_key = os.environ('LASTFM_API_KEY')
                    lastfm_api_secret = os.environ('LASTFM_API_SECRET')

                    if not all ([spotify_client_id, spotify_client_secret, lastfm_api_key, lastfm_api_secret]):
                        print("Missing API credentials in environment variables.")
                        sys.exit(1)

                    genre_caller = GenreCaller
            break

        except Exception as e:
            print(f"An error occurred: {e}")
            break