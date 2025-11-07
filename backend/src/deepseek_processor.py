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
        "model": "deepseek/deepseek-chat-v3-0324",
        "messages":[{"role": "system", "content": "You are an AI journey/roadtrip helper bot that, given a user's desires for their ideal journey,"
                                                    "will give the best filters from the Google Places API:\n"

                                                    "'restaurant', 'bar', 'cafe', bakery', 'shopping_mall', 'clothing_store', 'department_store', "
                                                    "'convenience_store', 'book_store', 'jewelry_store', 'store', 'florist', 'amusement_park', "
                                                    "'aquarium', 'art_gallery', 'bowling_alley', 'casino', 'movie_theater', 'museum', 'night_club', "
                                                    "'park', 'stadium', 'zoo', 'gym', 'tourist_attraction', 'spa', 'hotel', 'lodging', 'rv_park', and "
                                                    "'campground'.\n"

                                                    "Given the user's prompt, choose the best tags for their trip in a comma-separated list. You MUST "
                                                    "not return any other result. You should not add any additional comments to your resposne. The ideal "
                                                    "format for this result is shown below:\n"

                                                    "[TAG1],[TAG2],[TAG3],[TAG4]\n"

                                                    "You can add in more or less tags than just 4. As an example of a result, you can look at an example "
                                                    "result below:\n"

                                                    "bakery,aquarium,museum,zoo,tourist_attraction,shopping_mall"

                                                    "Here is an example prompt and the corresponding tag results with an informational explanation behind "
                                                    "the reasoning:\n"

                                                    "Input: I am going for vacation and would like to have a roadtrip where I can visit all of the museums, "
                                                    "shopping malls, and bakeries that are easily accessible on my route.\n"

                                                    "Output: museum,shopping_mall,bakery,tourist_attraction\n"

                                                    "Explanation: The user mentioned that they are going on vacation, so we included tourist_attraction as a "
                                                    "tag. Additionally, they explicitly stated they wanted to visit museums, shopping malls, and bakeries, so "
                                                    "those have all been added to the output."

                                                    "Here is another example prompt with an informational explanation:\n"

                                                    "Input: im not sure what is on the route but in general i would like to see anything interesting and "
                                                    "fun for my family\n"

                                                    "Output: amusement_park,aquarium,art_gallery,bowling_alley,movie_theater,museum,park,stadium,zoo,gym,spa,tourist_attraction\n"

                                                    "Explanation: The user is not sure about what they want to visit, except that they want to see fun "
                                                    "points of interest that are family friendly. Because of this broad query, we included all "
                                                    "entertainment results from the Google Places API except the non-family friendly locations, i.e. "
                                                    "casino and night_club.\n"

                                                    "Here is another example prompt with an informational explanation:\n"

                                                    "Input: i would like to mosques, train stations, and trendy restaurants\n"

                                                    "Output: restaurant\n"

                                                    "Explanation: The user requested to visit mosques, train stations, and 'trendy' restaurants. Mosques "
                                                    "train stations are not valid tags that we can give, so we cannot include them in our output list. "
                                                    "The user specifically requested 'trendy' restaurants; however, because we cannot filter restaurants "
                                                    "further, we can only give the tag restaurant.\n"

                                                    "Here is another example prompt with an informational explanation:\n"

                                                    "Input: i would like to go to the hardware store and the bank\n"

                                                    "Output:\n"

                                                    "Explanation: The user requested to visit the hardware store and the bank, but these are not valid "
                                                    "tags or locations we can direct them to. That means that we return an empty string.\n"


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