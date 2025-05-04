import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# Target URL
URL = "https://gdg.community.dev/gdg-on-campus-university-of-porto-porto-portugal/"

# Headers to simulate a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Fetch and parse the page
response = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

# --------------------------
# Scrape Team Members
# --------------------------
team = []

BASE_URL = "https://gdg.community.dev"

team_containers = soup.find_all("div", {"data-testid": "container-block-k9HYTOEmoCI"})
for member in team_containers:
    try:
        img_tag = member.find("img")
        image_url = img_tag.get("src") if img_tag else ""

        name_tag = member.find("p")
        name = name_tag.get_text(strip=True) if name_tag else "Unknown"

        role_tag = member.find("span", string=lambda x: x and ("Lead Organizer" in x or "Organizer" in x))
        role = role_tag.get_text(strip=True) if role_tag else "Member"

        profile_link_tag = member.find("a", string=lambda x: x and "View profile" in x)
        relative_url = profile_link_tag.get("href") if profile_link_tag else ""
        url = BASE_URL + relative_url if relative_url.startswith("/") else relative_url

        team.append({
            "nome": name,
            "cargo": role,
            "foto": image_url,
            "link": url
        })
    except Exception as e:
        print(f"Error parsing team member: {e}")

with open("./data/team.json", "w", encoding="utf-8") as f:
    json.dump(team, f, indent=2, ensure_ascii=False)

print(f"[✔] Saved {len(team)} team members to team.json")


# --------------------------
# Scrape Partners
# --------------------------
partners = []

partner_blocks = soup.find_all("a", {"data-testid": lambda x: x and x.startswith("container-block-")})
for partner in partner_blocks:
    try:
        url = partner.get("href")
        if url and url.startswith("https://gdg.community.dev/events/details/"):
            continue  # Skip event entries

        img_tag = partner.find("img")
        image_url = img_tag.get("src") if img_tag else ""

        # Try to infer name from image filename or domain
        if url:
            name = url.split("/")[-2] if "/" in url else url
        else:
            name = "Unknown"

        if image_url:
            partners.append({
                "nome": name,
                "foto": image_url,
                "link": url
            })
    except Exception as e:
        print(f"Error parsing partner: {e}")

with open("./data/partners.json", "w", encoding="utf-8") as f:
    json.dump(partners, f, indent=2, ensure_ascii=False)

print(f"[✔] Saved {len(partners)} partners to partners.json")

# --------------------------
# Scrape Events
# --------------------------
previous_events = []
upcoming_events = []

# Function to extract event details from a URL
def extract_event_details(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve page, status code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title_tag = soup.find("h1", {"class": "heading-styles__heading_28edq"})
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        # Extract date section by finding <h3> with text "When"
        when_header = soup.find("h3", string=lambda x: x and "When" in x)
        if when_header:
            # Get the parent container and find the next <p> with the actual date text
            date_container = when_header.find_next("p")
            date_text = date_container.get_text(separator=" ", strip=True) if date_container else "No Date"
        else:
            date_text = "No Date"

        print(f"Extracted date: {date_text}")

        return {
            "title": title,
            "date": date_text,
            "link": url,
        }

    except Exception as e:
        print(f"Error extracting details from {url}: {e}")
        return None

# Load event URLs from the file
event_urls = []
with open("data/event_links.txt", "r") as file:
    event_urls = file.readlines()

# Strip any extra whitespace/newlines
event_urls = [url.strip() for url in event_urls]

# Generate the events list
for url in event_urls:
    event_details = extract_event_details(url)
    if not event_details:
        continue

    date = event_details["date"]
    date_clean = date.replace('\u202f', ' ').strip()

    # Remove timezone
    if '(' in date_clean:
        date_clean = date_clean.split('(')[0].strip()

    # Try extracting typical full datetime
    match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4} \d{1,2}:\d{2} [AP]M)', date_clean)
    if match:
        start_time_str = match.group(1)
    else:
        # Handle cases like: "April 15 – 16, 2025 8:30 AM – 5:00 PM"
        try:
            # Match: month + first day
            date_match = re.search(r'([A-Za-z]+) (\d{1,2})\s*–.*?, (\d{4}) (\d{1,2}:\d{2} [AP]M)', date_clean)
            if date_match:
                month, day, year, time = date_match.groups()
                start_time_str = f"{month} {day}, {year} {time}"
            else:
                print(f"Could not parse date format: '{date_clean}'")
                continue
        except Exception as e:
            print(f"Error reconstructing multi-day event date: {e}")
            continue

    # Try parsing reconstructed or matched date
    try:
        raw_date = datetime.strptime(start_time_str, '%B %d, %Y %I:%M %p')
    except ValueError as e:
        print(f"Failed to parse date: '{start_time_str}' → {e}")
        continue

    # Categorize
    if raw_date < datetime.now():
        previous_events.append(event_details)
    else:
        upcoming_events.append(event_details)

previous_events.reverse()  # Reverse the list to have the most recent events first
upcoming_events.reverse()  # Reverse the list to have the most recent events first

# Save previous events to a JSON file
with open("./data/previousevents.json", "w", encoding="utf-8") as f:
    json.dump(previous_events, f, indent=2, ensure_ascii=False)

# Save upcoming events to a JSON file
with open("./data/upcomingevents.json", "w", encoding="utf-8") as f:
    json.dump(upcoming_events, f, indent=2, ensure_ascii=False)

print(f"[✔] Saved {len(previous_events)} previous events to previousevents.json")
print(f"[✔] Saved {len(upcoming_events)} upcoming events to upcomingevents.json")