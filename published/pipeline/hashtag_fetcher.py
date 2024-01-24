import re
import requests

class HashtagFetcher:
    def __init__(self):
        self.unique_hashtags = set()

    def fetch_hashtags(self, url):
        """Fetch hashtags from a single URL."""
        try:
            response = requests.get(url)
            self.extract_and_add_hashtags(response.text)
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

    def extract_and_add_hashtags(self, html_content):
        """Extract hashtags from HTML content and add them to the set."""
        hashtags = re.findall(r'#([a-zA-Z-_]{3,})', html_content)

        # Loop through the found hashtags
        for hashtag in hashtags:
            # Split each hashtag by capital letters
            split_hashtag = re.sub(r'(?<!^)(?=[A-Z])', ' ', hashtag).split()
            # Add each part of the split hashtag to the set
            for part in split_hashtag:
                if len(set(part)) >= 2:  # Check for at least two unique characters
                    self.unique_hashtags.add(part.lower())  # Convert to lowercase before adding
