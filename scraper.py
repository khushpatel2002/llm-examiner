import requests
from bs4 import BeautifulSoup
import re

# Send a GET request to the website
url = 'https://www.namaz.live/'
response = requests.get(url)

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the HTML elements containing the routes
route_elements = soup.find_all('a')

# Extract the routes from the elements
routes = set()
for route_element in route_elements:
    route = route_element.get('href')
    if route:
        routes.add(route)

routes = list(routes)
routes = [item for item in routes if not re.match(r'(http|https)://|^\S+@\S+\.\S+', item)]
routes

text = set()
for route in routes:

    route_url = url + route
    route_response = requests.get(route_url)

    if route_response.status_code == 404:
        print(f"Route {route} returned a 404 error. Skipping...")
        continue

    route_soup = BeautifulSoup(route_response.content, 'html.parser')

    route_text = ""
    for tag in route_soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        route_text += tag.get_text(separator=' ') + " "

    text.add(route_text)

type(text)

file_path = 'merged_strings.txt'

with open(file_path, 'w') as file:
    for string in text:
        file.write(string + '\n')

print(f"The strings have been merged and saved to {file_path}.")

with open(file_path, 'r') as file:
    file_contents = file.read()

print(file_contents)

