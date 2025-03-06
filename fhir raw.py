import requests
import json

FHIR_BASE_URL = "http://hapi.fhir.org/baseR4"  # Replace with your FHIR server URL
PATIENT_ENDPOINT = f"{FHIR_BASE_URL}/Patient?_count=5"  # Limit results to 5 patients

def get_raw_fhir_data():
    try:
        response = requests.get(PATIENT_ENDPOINT, headers={"Accept": "application/fhir+json"})
        response.raise_for_status()  # Raise error if request fails

        raw_data = response.json()  # Convert response to JSON
        print(json.dumps(raw_data, indent=2))  # Pretty print the raw JSON
        return raw_data

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving raw FHIR data: {e}")
        return None

if __name__ == "__main__":
    get_raw_fhir_data()
