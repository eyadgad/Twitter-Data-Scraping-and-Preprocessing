import nest_asyncio, os, shutil, json, time 
from datetime import datetime
from Scweet.scweet import Scweet
from utils import calc_n_splits, date_range, read_tweets, save_dict_to_csv
nest_asyncio.apply()

cookies = None # current library implementation depends on Nodriver cookies handling.
user_agent = None
concurrency = 5 # tweets and profiles fetching run in parallel (on multiple browser tabs at the same time). Adjust depending on ressources.
scroll_ratio = 100 # scrolling ratio while fetching tweets. adjust between 30 to 200 to optimize tweets fetching.
login = True # this is used for get_user_information method. X asks for login sometimes to display user profile.

proxy = None  #  add proxy settings. IF the proxy is public, you can provide empty username and password. Example: {"host": "1.2.3.4", "port": "8080", "username": "", "password": ""}
headless = False # Run the browser in headless mode (without GUI)
disable_images = True # disable loading images while fetching

save_directory = 'outputs'  # Directory where the results CSV file will be saved
custom_csv_filename = "tweets.csv"
cookies_directory = 'cookies' # directory where you want to save/load the cookies 'username_cookies.dat'

# Parameters for scraping
since_date = "2018-06-29"  # 🕐 Start date (YYYY-MM-DD) for scraping tweets
until_date = "2019-01-01"  # 🕐 End date (inclusive); tweets up to this date are include
query_words = None  # 🔍 Keywords to search for in tweets (can include hashtags)
to_account = None  # 🏷️ Specific account to filter tweets to (e.g., "elonmusk")
from_account = "cbcnews"  # 🏷️ Specific account to filter tweets from (e.g., "jack")
mention_account = None  # 🏷️ Specific account to filter mentions (e.g., "twitter")
language = "en"  # 🌐 Language filter (e.g., "en" for English)
limit_tweets = 1000  # 📄 Maximum number of tweets to fetch *per day* (not total)
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


os.makedirs(save_directory, exist_ok=True)

start = datetime.strptime(since_date, "%Y-%m-%d")
end = datetime.strptime(until_date, "%Y-%m-%d")

since_step = since_date
k=0
for i, until_step in enumerate(date_range(start, end)):
    if until_step == since_step:continue

    os.makedirs(cookies_directory, exist_ok=True)
    save_directory = f'outputs/{since_step}_{until_step}'
    if k>5:k=0
    env_path = f'environments/{k}.env'


    print(f"Processing:{since_step} to {until_step}")
    
    scweet = Scweet(
        proxy=proxy,
        cookies=cookies,
        cookies_path=cookies_directory,
        user_agent=user_agent,
        disable_images=disable_images,
        env_path=env_path,
        n_splits=calc_n_splits(since_step, until_step, days_interval) ,
        concurrency=concurrency,
        headless=headless,
        scroll_ratio=scroll_ratio
    )

    tweets = scweet.scrape(
        since = since_step,
        until = until_step,
        words = query_words,
        to_account = to_account,
        from_account = from_account,
        mention_account = mention_account,
        lang = language,
        limit = limit_tweets,
        display_type = display_type,
        resume = resume_scraping,
        hashtag = hashtag,
        filter_replies = filter_replies,
        proximity = proximity_search,
        geocode = geocode_location,
        minreplies = min_replies,
        minlikes = min_likes,
        minretweets = min_retweets,
        save_dir = save_directory,
        custom_csv_name = custom_csv_filename
    )     

    json_files = [os.path.join(save_directory, f) for f in os.listdir(save_directory) if "data" in f and f.endswith('.json')]
    data_dict = {"id":[],"name":[],"username": [], "time": [], "text": [], "counts": []}
    for json_file in json_files:
        with open(json_file, 'r') as file: json_data = json.load(file)
        data_dict = read_tweets(json_data, data_dict, csv=True, show_text=False)
        #os.remove(json_file)

    save_dict_to_csv(data_dict, os.path.join(save_directory, "tweets_from_json.csv"))
    shutil.rmtree(cookies_directory, ignore_errors=True)
    time.sleep(100)  # Sleep to avoid rate limiting

    since_step = until_step
    k+=1

