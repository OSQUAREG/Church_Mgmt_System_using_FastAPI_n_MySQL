import requests
import json


def save_openapi_spec(url, output_file):
    try:
        # Fetch the OpenAPI JSON specification
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON data
        openapi_spec = response.json()

        # Save the JSON data to a file
        with open(output_file, "w") as file:
            json.dump(openapi_spec, file, indent=4)

        print(f"OpenAPI specification saved to {output_file}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the OpenAPI specification: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing the JSON data: {e}")
    except IOError as e:
        print(f"Error saving the JSON data to a file: {e}")

