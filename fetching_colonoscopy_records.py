import requests
import json

def search_records(query, output_file):
    base_url = "https://api.fda.gov/device/event.json?api_key=TBzEbYiY4Pv9Q0aNLOaD1ayzrPiL9rmTjeOcZuHg"
    limit = 1000
    sort = "date_received:asc"

    # Step 1: Execute initial query
    initial_query_url = f"{base_url}&search={query}&limit={limit}&sort={sort}"
    response = requests.get(initial_query_url)
    
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code} {response.text}")
        return

    while response.status_code == 200:
        # Process the data in the response as needed
        process_data(response.json(), output_file)

        # Step 2: Extract Link header
        link_header = response.headers.get('Link')
        
        if link_header:
            # Step 3: Extract next page URL
            next_page_url = None
            parts = link_header.split(',')
            for part in parts:
                if 'rel="next"' in part:
                    next_page_url = part.split(';')[0].strip('<> ')
                    break

            if next_page_url:
                # Step 4: Use the extracted URL to obtain the next page of data
                response = requests.get(next_page_url)
            else:
                # No next page URL found, break the loop
                break
        else:
            # No more pages, break the loop
            break

def process_data(data, output_file):
    # Write the data to a JSON file
    with open(output_file, 'a') as file:
        for record in data.get('results', []):
            json.dump(record, file)
            file.write("\n")

if __name__ == "__main__":
    search_query = "device.generic_name.exact:(COLONOVIDEOSCOPE+%22VIDEO%20COLONOCOPE%20-%20I10%20STANDARD%22+%22VIDEO%20COLONOSCOPE%22+%22HDVIDEO%20COLONOSCOPE%203.8C%2013.2T%201700L%20FWJ%22+%22VIDEO%20COLONOSCOPE%203.8C%202.8C%2013.2T%20FWJ%22)"
    output_file = "results/colonoscope_reports.json"
    search_records(search_query, output_file)
