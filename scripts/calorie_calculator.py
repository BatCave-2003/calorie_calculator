import requests
import pandas as pd

def parse_item(item):
    """Parse the input string to extract quantity and food name."""
    parts = item.strip().split(' ')
    quantity = int(parts[0])
    food_name = ' '.join(parts[1:])
    return quantity, food_name

def fetch_nutrition_from_api(food_name):
    """Fetch nutritional data from the Nutritionix API."""
    # Replace 'YOUR_APP_ID' and 'YOUR_APP_KEY' with your actual credentials
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        'x-app-id': '4beb995c',
        'x-app-key': '2bc01e9052d6ce5069af4dd5c320329a',
        'Content-Type': 'application/json'
    }
    data = {
        "query": food_name,
        "timezone": "US/Eastern"
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    # Extract calories and protein from the response
    calories = result['foods'][0]['nf_calories']
    protein = result['foods'][0]['nf_protein']
    return calories, protein

def calculate_nutrition(food_items):
    """Calculate nutrition details for the given food items and return as a DataFrame."""
    items = food_items.split(',')
    data = []

    for item in items:
        quantity, food_name = parse_item(item)
        calories, protein = fetch_nutrition_from_api(food_name)
        data.append({
            'food_item': food_name,
            'food_quantity': quantity,
            'Kcal': calories * quantity,
            'protein': protein * quantity
        })

    df = pd.DataFrame(data, columns=['food_item', 'food_quantity', 'Kcal', 'protein'])
    return df

# if __name__ == '__main__':
    # Example input
def run():
    food_items = "1 apple, 12 almonds, 2 dosa, 5 scrambled eggs, 1 cup of rice"
    df = calculate_nutrition(food_items)
    print(df)