import requests
import json

def search_records(query, output_file):
    base_url = "https://api.fda.gov/device/event.json?api_key=TBzEbYiY4Pv9Q0aNLOaD1ayzrPiL9rmTjeOcZuHg"
    limit = 1000  # Set to the maximum allowed
    skip = 0  # Initialize skip counter

    while True:
        # Execute query with skip and limit
        query_url = f"{base_url}&count={query}&limit={limit}&skip={skip}"
        response = requests.get(query_url)

        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code} {response.text}")
            return

        data = response.json()
        process_data(data, output_file)

        results = data.get('results', [])
        if not results or len(results) < limit:
            break  # Break if no more results or fewer results than limit

        skip += limit  # Increment skip for the next batch of records

def process_data(data, output_file):
    # Write the data to a JSON file
    with open(output_file, 'a') as file:
        for record in data.get('results', []):
            json.dump(record, file)
            file.write("\n")

if __name__ == "__main__":
    search_query = "device.generic_name.exact"
    output_file = "results/generic_name_count.json"
    search_records(search_query, output_file)
