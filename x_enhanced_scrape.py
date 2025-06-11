from ScweetEnhanced.scweet import scrape
from ScweetEnhanced.utils import init_driver, log_in
from ScweetEnhanced.entity import CSVDurabilityHandler, Query
import os, datetime

headless = False
disable_images = True # disable loading images while fetching
proxy = None  #  add proxy settings. IF the proxy is public, you can provide empty username and password. Example: {"host": "1.2.3.4", "port": "8080", "username": "", "password": ""}

save_directory = 'outputs'  # Directory where the results CSV file will be saved
custom_csv_filename = 'enhanced_scweet_results.csv'  # Filename for the output CSV
env_path = '.env'

# Parameters for scraping
since_date = "2018-03-01"  # 🕐 Start date (YYYY-MM-DD) for scraping tweets
until_date = "2018-05-31"  # 🕐 End date (inclusive); tweets up to this date are include
query_words = None  # 🔍 Keywords to search for in tweets (can include hashtags)
to_account = None  # 🏷️ Specific account to filter tweets to (e.g., "elonmusk")
from_account = "cbcnews"  # 🏷️ Specific account to filter tweets from (e.g., "jack")
mention_account = None  # 🏷️ Specific account to filter mentions (e.g., "twitter")
language = "en"  # 🌐 Language filter (e.g., "en" for English)
limit_tweets = 3000  # 📄 Maximum number of tweets to fetch *per day* (not total)
display_type = "latest"  # 🧩 Display type on Twitter search: "Top", "Latest", or "Mixed"
resume_scraping = False  # 🔁 If True, resumes from where it left off using a .txt file
filter_replies = True  # ❌ If True, replies are excluded from the results
hashtag = None      # #️⃣ Specific hashtag to filter tweets (e.g., "#example")
proximity_search = False  # 📍 If True, fetches tweets based on proximity (location-based)
geocode_location = None  # 🌍 Location-based search using "lat,long,radius" (e.g., "37.7749,-122.4194,10km")
min_replies = 0  # 💬 Minimum number of replies a tweet must have to be included
min_likes = 0  # ❤️ Minimum number of likes a tweet must have
min_retweets = 0  # 🔁 Minimum number of retweets a tweet must have
days_interval = 1  # 📅 Interval in days for scraping (e.g., 1 day)

# Initialize browser driver
driver = init_driver(headless=headless, show_images= not disable_images, proxy = proxy)
log_in(driver, env=env_path)
os.makedirs(save_directory, exist_ok=True)

# Define query parameters (equivalent to your original Scweet setup)
query = Query(
    since=since_date,
    until=until_date,
    words=query_words,
    to_account=to_account,
    from_account=from_account,
    mention_account=mention_account,
    hashtag=hashtag,
    lang=language,
    limit=limit_tweets,
    display_type=display_type,
    resume=resume_scraping,
    replies_only=filter_replies,
    proximity=proximity_search,
    interval= datetime.timedelta(days=days_interval),
    geocode=geocode_location,
    min_replies=min_replies,
    min_likes=min_likes,
    min_retweets=min_retweets,
)  
# CSV Output Handler
csv_handler = CSVDurabilityHandler(file_name=custom_csv_filename, save_path=save_directory)

# Run the scraper
scrape(
    **vars(query),
    driver=driver,
    endure_handler=[csv_handler],
    save_images=False,
    filter_handler=None,          # you can define a custom filter class if needed
    proxy=proxy
)
