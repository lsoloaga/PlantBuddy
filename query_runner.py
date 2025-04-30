import openai
import requests
import json
import time
import sys
import os  
from urllib.parse import urlparse, parse_qs, urlencode 

def run_query(user_input):
    
    def fetch_plant_list():
        try:
            # Make the API request
    
            response = requests.get(query_url)
            print(query_url)
            response.raise_for_status()

            data = response.json()
            print(f"Found {data.get('total', '?')} plants")
            return data.get('data', [])
    
        except Exception as e:
            print(f"Error fetching plant list: {e}")
            return []

    def reformat_with_gpt(plant_data):
    
        client = openai.OpenAI(api_key="")

        prompt = f"""
        You are a plant assistant. Take the following plant data and return a short, friendly, well-formatted summary suitable for a beginner gardener.

        Format it as an informational paragraph.

        Here is the raw data:
        {json.dumps(plant_data, indent=2)}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a plant care assistant who formats data for humans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=400
            )

            return response.choices[0].message.content.strip()
    
        except Exception as e:
            print(f"Error formatting with GPT: {e}")
            return "Failed to format plant data."

    print(user_input)
    def clean_url(url):
        parsed = urlparse(url)
        query_dict = parse_qs(parsed.query)

        # Remove parameters with empty values
        cleaned = {k: v[0] for k, v in query_dict.items() if v[0].strip() != ""}

        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(cleaned)}"
    # === CONFIGURATION ===
    openai.api_key = ""
    BASE_URL = "https://perenual.com/api/v2/species-list"
    PLANT_API_KEY = ""  



    prompt = f"""
    You are a system that generates query URLs for the following API:
    {BASE_URL}?key={PLANT_API_KEY}&q=&edible=&cycle=&watering=&sunlight=&indoor=&hardiness=

    Based on the user's request: "{user_input}"

    Your job is to fill in the appropriate query parameters based on their request.
    Return only the full, properly URL-encoded URL.
    """.strip()

    client = openai.OpenAI(api_key="")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": """
    You are a URL generation assistant for a plant API.

    Your job is to take a user's natural language request and translate it into a properly URL-encoded query string using the allowed parameters and values listed below.

    You MUST only use the exact valid values for each parameter — no variations or synonyms.

    **API Endpoint Format:**
    https://perenual.com/api/v2/species-list?key={PLANT_API_KEY}&q=&edible=&poisonous=&cycle=&watering=&sunlight=&indoor=&hardiness=

    **Valid Values:**

    - edible: 1 (edible), 0 (not edible)
    - poisonous: 1 (poisonous), 0 (not poisonous)
    - cycle: perennial, annual, biennial, biannual
    - watering: frequent, average, minimum, none
    - sunlight: full_shade, part_shade, sun-part_shade, full_sun
    - indoor: 1 (true), 0 (false)
    - hardiness: integer 1–13

    **Guidelines:**
    - Infer indoor=1 if "indoors", "home", "windowsill" or "apartment" is mentioned.
    - Infer indoor=0 if "garden", "backyard", "balcony", or "porch" is mentioned.
    - Convert common watering terms to valid values: "low" or "minimal" → "minimum", "regular" → "average", etc.
    - Convert sunlight terms: "direct sunlight" → "full_sun", "partial shade" → "part_shade", etc.
    - Infer edible=1 if "fruit", "vegetables", or "herbs" is mentioned 
    - Leave any parameter blank (empty) if not inferable or not mentioned.
    - Return only the final URL, nothing else.
    """},

            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )   

    # === PRINT RESULT ===
    query_url = response.choices[0].message.content.strip()
    print("Generated Query URL:")
    query_url = clean_url(query_url)
    print("Generated clean Query URL:")
    print(query_url)

    #==== Start the API calls to plant====
    print("Fetching plant list...")
    plants = fetch_plant_list()
    print(f"Fetched {len(plants)} plants")
    
    if not plants:
        print("No plants found matching the criteria.")
        
        return
    
    num_plants = min(5, len(plants))
    
        # Fetch and display details for the requested number of plants
    summaries = []

    for i in range(num_plants):
        plant = plants[i]
        print(f"\nFetching details for plant {i+1}/{num_plants}: {plant.get('common_name')} (ID: {plant.get('id')})...")
        details = get_plant_details(plant.get('id'))
    
        if not details:
            summaries.append("No details available.")
            continue

        formatted = reformat_with_gpt(details)
       #summaries.append(formatted)

    
        image_url = None
        if details.get("default_image"):
            image_url = details["default_image"].get("medium_url")

    
        summaries.append({"summary": formatted, "image": image_url})


        if i < num_plants - 1:
            time.sleep(1)

    return summaries



def get_plant_details(plant_id):
    """
    Fetches detailed information about a specific plant using its ID.
    """
    plant_api_key = ""
    
    url = f"https://perenual.com/api/v2/species/details/{plant_id}"
    params = {"key": plant_api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching details for plant ID {plant_id}: {e}")
        return None

def display_plant_info(plant_details):
    """
    Displays comprehensive information about a plant.
    """
    if not plant_details:
        print("No plant details available.")
        return
    
    print("\n" + "="*50)
    print(f"ID: {plant_details.get('id')}")
    print(f"Common Name: {plant_details.get('common_name')}")
    ##print(f"Scientific Name: {', '.join(plant_details.get('scientific_name', []))}")
    
    if plant_details.get('other_name'):
        other_names = plant_details.get('other_name')
        if isinstance(other_names, list):
            print(f"Other Names: {', '.join(other_names)}")
        else:
            print(f"Other Names: {other_names}")
    
    # if plant_details.get('family'):
        #print(f"Family: {plant_details.get('family')}")
    
    if plant_details.get('type'):
        print(f"Type: {plant_details.get('type')}")
    
    print(f"Cycle: {plant_details.get('cycle', 'Not specified')}")
    
        # Watering information
    print(f"Watering: {plant_details.get('watering', 'Not specified')}")
    if plant_details.get('watering_general_benchmark'):
        benchmark = plant_details.get('watering_general_benchmark')
        print(f"Watering Schedule: Every {benchmark.get('values')} {benchmark.get('unit')}")
    
    # Sunlight information
    if plant_details.get('sunlight'):
        sunlight = plant_details.get('sunlight')
        if isinstance(sunlight, list):
            print(f"Sunlight: {', '.join(sunlight)}")
        else:
            print(f"Sunlight: {sunlight}")
    
    if plant_details.get('hardiness'):
        hardiness = plant_details.get('hardiness')
        print(f"Hardiness Zone: {hardiness.get('min')} to {hardiness.get('max')}")
    
    # Growth information
    if plant_details.get('growth_rate'):
        print(f"Growth Rate: {plant_details.get('growth_rate')}")
    
    if plant_details.get('maintenance'):
        print(f"Maintenance: {plant_details.get('maintenance')}")
    
    if plant_details.get('care_level'):
        print(f"Care Level: {plant_details.get('care_level')}")
    
    # Edibility information
    print(f"Edible Fruit: {plant_details.get('edible_fruit', False)}")
    #print(f"Edible Leaf: {plant_details.get('edible_leaf', False)}")
    
        # Display other characteristics
        #characteristics = [
            #("Medicinal", plant_details.get('medicinal')),
            #("Drought Tolerant", plant_details.get('drought_tolerant')),
            #("Salt Tolerant", plant_details.get('salt_tolerant')),
            #("Thorny", plant_details.get('thorny')),
            #("Invasive", plant_details.get('invasive')),
            #("Tropical", plant_details.get('tropical')),
            #("Indoor", plant_details.get('indoor')),
            #("Poisonous to Humans", plant_details.get('poisonous_to_humans')),
            #("Poisonous to Pets", plant_details.get('poisonous_to_pets'))
        #]
    
        #print("\nCharacteristics:")
        #for name, value in characteristics:
            # if value is not None:
                #print(f"- {name}: {'Yes' if value else 'No'}")
    
    ''' # Display image URL if available
    if plant_details.get('default_image') and plant_details.get('default_image').get('medium_url'):
    print(f"\nImage: {plant_details.get('default_image').get('medium_url')}")
    
    # Display description if available
    if plant_details.get('description'):
        print(f"\nDescription: {plant_details.get('description')}")
    '''
    print("="*50)

'''def main():
    print("Fetching plant list...")
    plants = fetch_plant_list()
    print(f"Fetched {len(plants)} plants")
    
    if not plants:
        print("No plants found matching the criteria.")
        return
    
    num_plants = min(2, len(plants))
    
    # Fetch and display details for the requested number of plants
    for i in range(num_plants):
        plant = plants[i]
        print(f"\nFetching details for plant {i+1}/{num_plants}: {plant.get('common_name')} (ID: {plant.get('id')})...")
        details = get_plant_details(plant.get('id'))
        display_plant_info(details)
        
        # Add a small delay between API requests to avoid rate limiting
        if i < num_plants - 1:
            time.sleep(1)
    '''
    #if __name__ == "__main__":
    #main()x


