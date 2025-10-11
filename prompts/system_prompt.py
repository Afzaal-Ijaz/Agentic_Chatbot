

classifier_prompt = f"""
    Classify the following query into one of these categories:
    [flight_search, hotel_search, destination_recommendation, non_travel_query].
    Respond with only one label.

    Query: {user_message}
    """
