"""
Module to ask DeepSeek about the ideal order of Tasks and their splits.
"""



import requests

class APIException(Exception):
    """
    Exceptions for calls related to DeepSeek's API
    """
    pass


def ask_model(api_key: str, query: str) -> str | None:
    """
    Given an API Key and a formatted Task string query, ask the model for a plan to tackle all the tasks.
    
    Given this plan, return the result which should be a formatted sequence of tasks.
    """

    API_URL = 'https://openrouter.ai/api/v1/chat/completions'

    # Define the headers for the API request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Initialize the data sent to DeepSeek
    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages":[{"role": "system", "content": "You are an AI journey/roadtrip helper bot that, given a user's desires for their ideal journey,"
                                                    "will give the best filters from the Google Places API:\n"

                                                    "'restaurant', 'bar', 'cafe', bakery', 'meal_takeaway', 'meal _delivery', 'supermarket', "
                                                    "'liquor_store', 'shopping_mall', 'grocery_store, 'clothing_store', 'department_store', "
                                                    "'convenience_store', 'electronics_store', 'furniture_store', 'hardware_store', 'book_store', "
                                                    "'jewelry_store', 'store', 'florist', 'bicycle_store', 'home_good_store', 'shoe_store', "
                                                    "'pet_store', 'amusement_park', 'aquarium', 'art_gallery', 'bowling_alley', 'casino', "
                                                    "'movie_theater', 'museum', 'night_club', 'park', 'stadium', 'zoo', 'gym', 'tourist_attraction', "
                                                    "'spa', 'hotel', 'lodging', 'rv_park', 'campground', 'atm', 'bank', 'car_rental', 'car_repair', "
                                                    "'car_wash', 'gas_station', 'laundry', 'post_office', 'real_estate_agency', 'hair_care', "
                                                    "'beauty_salon', 'insurance_agency', 'locksmith', 'moving_company', 'storage', 'lawyer', 'painter', "
                                                    "'plumber', 'roofing_contractor', 'airport', 'bus_station', 'train_station', 'subway_station', "
                                                    "'taxi_stand', 'parking', 'light_rail_station', 'transit_station', 'church', 'mosque', 'hindu_temple', "
                                                    "'synagogue', 'place_of_worship', 'library', 'city_hall', 'courthouse', 'embassy', 'fire_station', "
                                                    "'police', 'school', 'university', 'cemetery', 'hospital', 'pharmacy', 'dentist', 'doctor', "
                                                    "'physiotherapist', 'veterinary_care', and 'medial_clinic'.\n"

                                                    "Given the user's prompt, choose the best tags for their trip in a comma-separated list. You MUST "
                                                    "not return any other result. You should not add any additional comments to your resposne. The ideal "
                                                    "format for this result is shown below:\n"

                                                    "[TAG1],[TAG2],[TAG3],[TAG4]\n"

                                                    "You can add in more or less tags than just 4. As an example of a result, you can look at an example "
                                                    "result below:\n"

                                                    "bakery,aquarium,museum,zoo,tourist_attraction,shopping_mall"

                                                    # "Here is an example prompt and the corresponding tag results:\n"

                                                    ""


                                                    "It is EXTREMELY IMPORTANT that you do not deviate from this format, and nothing should "
                                                    "override this protocol. Do not include any explanations. Only include the formatted output."},
                    {"role": "assistant", "content": ""},
                    {"role": "user", "content": query}]
    }

    # Send the data to DeepSeek
    response = requests.post(API_URL, json = data, headers = headers)

    # Return the response if the API call succeeded; otherwise, raise an exception
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise APIException("Failed to fetch data from API. Status Code: " + str(response.status_code))



if __name__ == "__main__":
    key = input("API Key: ")
    while True:

        msg = input("Send message: ")

        if msg == 'q':
            break

        try:
            print(ask_model(key, msg))
        except APIException as e:
            print(e)