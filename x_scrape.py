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

    for i, until_step in enumerate(date_range(start, end, 15)):
        if until_step == since_step:continue

        shutil.rmtree(cookies_directory, ignore_errors=True)
        os.makedirs(cookies_directory, exist_ok=True)

        save_directory = f'{from_account}/{since_step}_{until_step}'
        if k >= len(envfiles): k=0
        env_path = f'environments/{k}.env'
        
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
            os.remove(json_file)

        save_dict_to_csv(data_dict, os.path.join(save_directory, "tweets_from_json.csv"))
        
        since_step = until_step
        k+=1
        time.sleep(20)

    l = [os.path.join(from_account, i) for i in os.listdir(from_account) ]
    tweets_files = [os.path.join(i, custom_csv_filename) for i in l if os.path.exists(os.path.join(i, custom_csv_filename))]

    # replace with your actual file list
    final_csv_file = f"{from_account}_tweets.csv"
    merge_csv_files(tweets_files, final_csv_file)

    df = pd.read_csv(final_csv_file, dtype={"tweetId": str})
    df['url_id'] = df['Tweet URL'].apply(extract_id_from_url)

    # Replace tweet_id with url_id if they don't match and url_id is valid
    df['tweetId'] = df.apply(
        lambda row: row['url_id'] if row['url_id'] and row['tweetId'] != row['url_id'] else row['tweetId'],
        axis=1
    )

    df['Text'] = df['Text'].str.replace('\n', ' ', regex=False)
    df['Text'] = df['Text'].str.replace('\r', ' ', regex=False)
    df['Text'] = df['Text'].str.replace('http', ' http', regex=False)


    df.drop(columns=['url_id'], inplace=True)
    df.drop(columns=['Embedded_text'], inplace=True, errors='ignore')
    df.drop(columns=['Emojis'], inplace=True, errors='ignore')
    df.drop(columns=['Image link'], inplace=True, errors='ignore')
    df.drop_duplicates(subset='tweetId', inplace=True)
    df.sort_values(by='Timestamp', inplace=True)

    df.to_csv(final_csv_file, index=False)
