"""Generate the 180-row cleaned Tricity restaurant catalogue used by TasteTrail."""
from pathlib import Path
import csv
import random

random.seed(73)
cuisines = {
    "North Indian": ("Butter Chicken; Dal Makhani; Tandoori Platter", "Curries, kebabs, biryani, breads"),
    "Cafe": ("Cold Brew; Avocado Toast; Pancake Stack", "Coffee, breakfast bowls, sandwiches, desserts"),
    "Italian": ("Truffle Pasta; Burrata Pizza; Tiramisu", "Pizza, pasta, risotto, desserts"),
    "Chinese": ("Chilli Paneer; Dimsum; Hakka Noodles", "Noodles, dimsum, stir-fry, soups"),
    "South Indian": ("Masala Dosa; Mini Idli; Filter Coffee", "Dosa, idli, vada, coffee"),
    "Punjabi": ("Amritsari Kulcha; Chole; Lassi", "Thalis, curries, breads, desserts"),
    "Continental": ("Grilled Chicken; Caesar Salad; Chocolate Fondant", "Salads, grills, pasta, desserts"),
    "Asian": ("Sushi Roll; Thai Curry; Ramen", "Sushi, Thai curry, ramen, bowls"),
    "Bakery": ("Sourdough; Red Velvet Cake; Croissant", "Cakes, pastries, breads, coffee"),
    "Fast Food": ("Loaded Burger; Peri Peri Fries; Wrap", "Burgers, wraps, fries, shakes"),
}
prefixes = ["Olive", "Copper", "Saffron", "Willow", "Urban", "Cedar", "Mango", "Mint", "Blue", "Curry", "Basil", "Roast", "Amber", "Maple", "Pine"]
suffixes = ["Table", "Kitchen", "Cafe", "Bistro", "Social", "House", "Grill", "Corner", "Stories", "Terrace", "Collective", "Diner"]
locations = {
    "Chandigarh": ["Sector 7", "Sector 9", "Sector 17", "Sector 22", "Sector 26", "Sector 35", "Sector 43"],
    "Mohali": ["Phase 3B2", "Phase 5", "Phase 7", "Phase 10", "Sector 70", "Sector 79", "Airport Road"],
    "Panchkula": ["Sector 5", "Sector 8", "Sector 11", "Sector 15", "Sector 20", "MDC Sector 4"],
}
images = [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1445116572660-236099ec97a0?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
]
rows, used = [], set()
for idx in range(180):
    city = ["Chandigarh", "Mohali", "Panchkula"][idx % 3]
    cuisine = list(cuisines)[idx % len(cuisines)]
    area = locations[city][idx % len(locations[city])]
    name = f"{prefixes[idx % len(prefixes)]} {suffixes[(idx // len(prefixes)) % len(suffixes)]}"
    if name in used: name += f" {area.replace(' ', '')}"
    used.add(name)
    popular, menu = cuisines[cuisine]
    veg = "Yes" if cuisine in ["Cafe", "South Indian", "Punjabi", "Bakery"] or random.random() < .42 else "No"
    cost = random.randrange(350, 2401, 50)
    rating = round(random.uniform(3.8, 4.9), 1)
    rows.append({"ID": idx + 1, "Restaurant": name, "City": city, "Area": area, "Cuisine": cuisine, "Rating": rating, "Cost": cost, "Veg": veg, "Delivery": "Yes" if random.random() < .78 else "No", "Address": f"SCO {random.randint(12, 345)}, {area}, {city}, Punjab", "Phone": f"+91 98{random.randint(10000000, 99999999)}", "Timings": random.choice(["9 AM - 11 PM", "11 AM - 11:30 PM", "12 PM - 12 AM", "8 AM - 10:30 PM"]), "Menu": menu, "Description": f"A well-loved {cuisine.lower()} destination in {area}, known for relaxed service, fresh flavours, and an inviting setting.", "Popular_Dishes": popular, "Popularity": random.randint(60, 99), "Image": images[idx % len(images)]})

output = Path(__file__).with_name("tricity_restaurants.csv")
with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader(); writer.writerows(rows)
print(f"Wrote {len(rows)} cleaned restaurants to {output}")
