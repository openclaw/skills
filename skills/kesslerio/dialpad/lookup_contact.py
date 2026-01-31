import os
import json
import urllib.request
import urllib.error

API_KEY = "3SHWcy2ThPfhUvkkhNEvgnmGKJvJ3qzCSLZYqJ3QX8yWrHrrUyRuvzbqHqEHbumsKsjasb9VfhcJffRxRHRHPr5DhtwaWx4LBk9n"
BASE_URL = "https://dialpad.com/api/v2"

def get_contact_name(phone_number):
    """Try to resolve a phone number to a contact name via Dialpad API."""
    # Dialpad expects E.164, but for searching it can be flexible.
    # We use the /contacts endpoint with a search query.
    query = phone_number.replace("+", "")
    url = f"{BASE_URL}/contacts?query={query}"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            items = data.get("items", [])
            if items:
                # Return the first matching name
                contact = items[0]
                first = contact.get("first_name", "")
                last = contact.get("last_name", "")
                name = f"{first} {last}".strip()
                return name or "Known Contact (No Name)"
            return None
    except Exception as e:
        print(f"Contact lookup error: {e}")
        return None

if __name__ == "__main__":
    test_num = "+14158235304" # Testing with Martin's number
    name = get_contact_name(test_num)
    print(f"Lookup for {test_num}: {name}")
