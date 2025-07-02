import pandas as pd, datetime, re, os, time, csv

def calc_n_splits(since, until, interval):
    if interval <= 1 or not interval: return -1
    since = datetime.datetime.strptime(since, "%Y-%m-%d")
    until = datetime.datetime.strptime(until, "%Y-%m-%d")
    delta = until - since
    n_splits = (delta.days // interval) + 1
    return n_splits

def date_range(start_date, end_date, step_days=15):
    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime("%Y-%m-%d") 
        current_date += datetime.timedelta(days=step_days)   
    yield end_date.strftime("%Y-%m-%d")

def read_tweets(data, data_dict, csv=False, show_text=False):
    if csv: kewords = ["handle", "postdate", "text", "embedded", "reply_cnt", "like_cnt", "retweet_cnt","username"]
    else: kewords = ["UserScreenName", "Timestamp", "Text", "Embedded_text", "Comments", "Likes", "Retweets","UserName"]
    for key, value in data.items():
        tweet_id = key
        tweet_username = value[kewords[0]]
        tweet_time = value[kewords[1]]
        tweet_text = value[kewords[2]]
        tweet_embedded_text = value[kewords[3]]
        tweet_comment_count = value[kewords[4]]
        tweet_like_count = value[kewords[5]]
        tweet_retweet_count = value[kewords[6]]
        tweet_account_name = value[kewords[7]]
        data_dict["id"].append(tweet_id)
        data_dict["name"].append(tweet_account_name)
        data_dict["username"].append(tweet_username)
        data_dict["time"].append(tweet_time)
        data_dict["text"].append(tweet_text)
        data_dict["counts"].append({
            "comments": tweet_comment_count,
            "likes": tweet_like_count,
            "retweets": tweet_retweet_count
        })
        if show_text:
            print(f"ID: {tweet_id:<20} Username: {tweet_username:<20} (comments, likes, retweets) {tweet_comment_count:<4}, {tweet_like_count:<4}, {tweet_retweet_count:<4}")
            print(f"Text: {tweet_text}")
    return data_dict

def save_dict_to_csv(data_dict, path):
    data_dict["id"], data_dict["name"], data_dict["username"], data_dict["time"], data_dict["text"], data_dict["counts"] = zip(*sorted(zip(data_dict["id"], data_dict["name"], data_dict["username"], data_dict["time"], data_dict["text"], data_dict["counts"]), key=lambda x: pd.to_datetime(x[3])))
    head="tweetId,UserScreenName,UserName,Timestamp,Text,Embedded_text,Emojis,Comments,Likes,Retweets,Image link,Tweet URL"
    # save the data to a CSV file
    with open(path, "w", encoding="utf-8", newline="") as file:
        file.write(head + "\n")
        for indx in range(len(data_dict["username"])):
            counts = data_dict["counts"][indx]

            tweet_id = data_dict["id"][indx]
            tweet_screen_name = data_dict["username"][indx]
            tweet_username = data_dict["name"][indx]
            tweet_time = data_dict["time"][indx]
            tweet_text = data_dict["text"][indx]
            tweet_embedded_text = " "
            tweet_emojis = " "
            tweet_comment_count = counts["comments"]
            tweet_like_count = counts["likes"]
            tweet_retweet_count = counts["retweets"]
            tweet_image_link = " "
            tweet_url = f"https://twitter.com/{tweet_username}/status/{tweet_id}"
            row = f"{tweet_id},{tweet_screen_name},{tweet_username},{tweet_time},{tweet_text},{tweet_embedded_text},{tweet_emojis},{tweet_comment_count},{tweet_like_count},{tweet_retweet_count},{tweet_image_link},{tweet_url}\n"
            file.write(row)
    print(f"Data saved to {path}")

def extract_id_from_url(url):
    match = re.search(r'status/(\d+)', str(url))
    return match.group(1) if match else None

def merge_csv_files(tweets_files, final_csv_file):
        header_written = False
        with open(final_csv_file, 'w', newline='', encoding='utf-8') as fout:
            writer = None
            for csv_file in tweets_files:
                with open(csv_file, 'r', encoding='utf-8') as fin:
                    reader = csv.reader(fin)
                    header = next(reader)
                    if not header_written:
                        writer = csv.writer(fout)
                        writer.writerow(header)
                        header_written = True
                    for row in reader: writer.writerow(row)