import nest_asyncio, os, shutil, json, time, pandas as pd
from datetime import datetime
from Scweet.scweet import Scweet
from utils import calc_n_splits, date_range, read_tweets, save_dict_to_csv, extract_id_from_url, merge_csv_files
nest_asyncio.apply()

cookies = None # current library implementation depends on Nodriver cookies handling.
user_agent = None
concurrency = 5 # tweets and profiles fetching run in parallel (on multiple browser tabs at the same time). Adjust depending on ressources.
scroll_ratio = 100 # scrolling ratio while fetching tweets. adjust between 30 to 200 to optimize tweets fetching.
login = True # this is used for get_user_information method. X asks for login sometimes to display user profile.

proxy = None  #  add proxy settings. IF the proxy is public, you can provide empty username and password. Example: {"host": "1.2.3.4", "port": "8080", "username": "", "password": ""}
headless = False # Run the browser in headless mode (without GUI)
disable_images = True # disable loading images while fetching

custom_csv_filename = "tweets.csv"
cookies_directory = 'cookies' # directory where you want to save/load the cookies 'username_cookies.dat'

# Parameters for scraping
query_words = None  # 🔍 Keywords to search for in tweets (can include hashtags)
to_account = None  # 🏷️ Specific account to filter tweets to (e.g., "elonmusk")
mention_account = None  # 🏷️ Specific account to filter mentions (e.g., "twitter")
language = "en"  # 🌐 Language filter (e.g., "en" for English)
limit_tweets = 3000  # 📄 Maximum number of tweets to fetch per day (not total)
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


from_accounts = ["CIBC", "Scotiabank", "NationalBank"]
from_accounts = ["CIBC", "Scotiabank", "NationalBank"]

idx = -1
for i in range(len(from_accounts)):
    if not os.path.exists(from_accounts[i]):
        idx = i-1 if i > 0 else 0
        break

from_accounts = from_accounts[idx:] 
envfiles = os.listdir("./environments") 
for from_account in from_accounts:
    since_date = "2018-01-01"  # 🕐 Start date (YYYY-MM-DD) for scraping tweets 290,213
    until_date = "2021-01-01"  # 🕐 End date (inclusive); tweets up to this date are included
    if os.path.exists(from_account) and len(os.listdir(from_account)) > 0:
        since_date = max([datetime.strptime(i.split('_')[0], '%Y-%m-%d') for i in os.listdir(from_account)]).strftime('%Y-%m-%d')

    start = datetime.strptime(since_date, "%Y-%m-%d")
    end = datetime.strptime(until_date, "%Y-%m-%d")
    since_step = since_date
    k=0