import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

url = "https://www.rentfaster.ca/api/search.json?proximity_type=location-city&novacancy=0&city_id=1&beds=1"

response = requests.get(url)

rentfaster_listings = {}

if response.status_code == 200:
    data = response.json()["listings"]
    rentfaster_listings = data
    # print(data)
else:
    print("Failed to retrieve data from Rentfaster API")


# Define the Wikipedia URL
wikipedia_url = "https://en.wikipedia.org/wiki/List_of_neighbourhoods_in_Calgary"

# Send an HTTP GET request to the Wikipedia page
res = requests.get(wikipedia_url)

# Parse the HTML content of the page
soup = BeautifulSoup(res.text, "html.parser")

# Find the table with the specified class
tables = soup.findAll("table", {"class": "wikitable"})
target_table = tables[1]

# Initialize empty lists to store the extracted data
communities = []
quadrants = []
communityByQuadrant = []

# Iterate through the rows of the table
for row in target_table.find_all("tr")[1:]:  # Skip the header row
    columns = row.find_all("td")
    if len(columns) >= 2:  # Ensure there are at least two columns
        community = columns[0].get_text(strip=True)
        quadrant = columns[1].get_text(strip=True)
        communities.append(community)
        quadrants.append(quadrant)

        communityByQuadrant.append([community, quadrant])

# Create a dictionary mapping communities to quadrants
community_to_quadrant = dict(zip(communities, quadrants))

# Iterate through Rentfaster listings and add the 'quadrant' key
for listing in rentfaster_listings:
    community_name = listing["community"]
    if community_name in community_to_quadrant:
        listing["quadrant"] = community_to_quadrant[community_name]
    else:
        listing["quadrant"] = "Unknown"


# Assuming 'rentfaster_listings' contains the JSON data from Rentfaster
df = pd.DataFrame(rentfaster_listings)


def preprocess_price(price_str):
    # If the price is a range (e.g., "1000 - 1500"), take the average
    if "-" in price_str:
        price_range = price_str.split("-")
        return (int(price_range[0]) + int(price_range[1])) / 2
    else:
        return int(price_str)


# # Apply the preprocessing function to the 'price' column
df["price"] = df["price"].apply(preprocess_price)

# Calculate the average price
average_price = df["price"].mean()
print(f"Average Price: ${average_price:.2f}")

average_price_by_quadrant = df.groupby("quadrant")["price"].mean().reset_index()
print(average_price_by_quadrant)

# fig = px.bar(df, x="price", y="title", title="Average Price by Location")
# fig.show()

fig = px.bar(
    average_price_by_quadrant,
    x="quadrant",
    y="price",
    title="Average Price by Quadrant",
)

# Customize the chart if needed (e.g., labels, colors)
fig.update_xaxes(title_text="Quadrant")
fig.update_yaxes(title_text="Average Price")

# Calculate the average price per bedroom per quadrant
average_price_per_bedroom = (
    df.groupby(["quadrant", "bedrooms"])["price"].mean().reset_index()
)
print(average_price_by_quadrant)

# Plot the data
fig2 = px.bar(
    average_price_per_bedroom,
    x="quadrant",
    y="price",
    color="bedrooms",
    title="Average Price by Quadrant and Number of Bedrooms",
)

# Customize the chart if needed (e.g., labels, colors)
fig2.update_xaxes(title_text="Quadrant")
fig2.update_yaxes(title_text="Average Price")
fig2.update_layout(legend_title_text="Bedrooms")


# Show the plots
fig.show()
fig2.show()
