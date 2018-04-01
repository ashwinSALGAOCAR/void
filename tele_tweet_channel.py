#!/usr/bin/env python
#code to fetch a particular users Tweets in the last 24 hours and liking it if not liked before.
import tweepy, datetime, time, pytz, yaml, telegram, requests, urllib3
from config import access_key, access_secret, consumer_key, consumer_secret, telegram_PIN

#Fetch the Twitter keys and secrets for the script ti access Twitter.

AUTH = tweepy.OAuthHandler(consumer_key, consumer_secret)
AUTH.set_access_token(access_key, access_secret)

API = tweepy.API(AUTH)

#Fetch the Telegram token for the script to access Telegram.

BOT = telegram.Bot(token=telegram_PIN)

CONFIG_FILE = 'users.yaml'

def get_tweets(username):
#    request = requests.get(url, stream=True)
#    print request
    page = 1
    deadend = False
    max_tweets = 10
    http = urllib3.PoolManager()
    
    while True:

        for tweet in tweepy.Cursor(API.user_timeline,
                                   username,
                                   page = page,
                                   include_entities = True,
                                   tweet_mode='extended').items():
            
            #24 hour Format.
            fmt1 = '%Y-%m-%d %H:%M:%S'
            #12 hour Format.
            fmt = '%Y-%m-%d %I:%M %p %Z'
            #Set Timezone variables to store Twitter's UTC Time and converting it to IST Time.
            utc = pytz.timezone('UTC')
            ist = pytz.timezone('Asia/Calcutta')
            utc_date=utc.localize(tweet.created_at)
            ist_date  = utc_date.astimezone(ist)


            if (datetime.datetime.now() - tweet.created_at).days <= 1:

                tw_handle = '@' + API.get_user(tweet.user.id_str).screen_name
                rtw_handle = tw_handle
                message = "\n\nLike/Retweet/Comment at https://twitter.com/{0}/status/{1}"
                visit_link = "\n\nOr visit the link in the {0} directly via:"
                no_url = '\n\nNo Urls in this Tweet.'

                #If the Tweet is a ReTweet, it gets truncated, hence we print the tweet._json
                if 'retweeted_status' in tweet._json:

                    screen_name, tweet_id = get_tweet_details(tweet.retweeted_status)
                    rtw_handle  += ' RT @' + screen_name          #Appends RT @ to the Message.
                    likes = tweet.retweeted_status.favorite_count

                    if tweet.retweeted_status.entities['urls']:

                        url_list = get_url_list(tweet.retweeted_status)
                        StoryUrl = message.format(screen_name, tweet_id)
                        StoryUrl += visit_link.format("Retweet") + str(url_list)
                                                                           
                    else:
                        StoryUrl = message.format(screen_name, tweet_id) + no_url

                #Else if it is a Tweet, simply paste the full text.
                else:
                    
                    screen_name, tweet_id = get_tweet_details(tweet)
                    likes = tweet.favorite_count

                    if tweet.entities['urls']:

                        url_list = get_url_list(tweet)
                        StoryUrl = message.format(screen_name, tweet_id)
                        StoryUrl += visit_link.format("Tweet") + str(url_list)
                        
                    else:
                        StoryUrl = message.format(screen_name, tweet_id) + no_url


                status = ist_date.strftime(fmt)
                status += make_status(tw_handle, rtw_handle, likes, tweet, StoryUrl)
                send_to_telegram(message=status)
            else:
                deadend = True
                return
        if not deadend:
            page+=1
            time.sleep(5)

def get_tweet_details(tweet):

    screen_name = API.get_user(tweet.user.id_str).screen_name
    tweet_id = tweet.id_str
    return screen_name, tweet_id

def get_url_list(tweet):

    urllist = []
    for url in tweet.entities['urls']:
        urllist.append(url['expanded_url'])
    return urllist

def make_status(tw_handle, rtw_handle, likes, tweet, StoryUrl):

    if 'retweeted_status' in tweet._json:
        tweet_text = "\n" + rtw_handle
        tweet_text += "\n"+ tweet._json['retweeted_status']['full_text']
    else:
        tweet_text = "\n" + tw_handle
        tweet_text += "\n"+ tweet.full_text
        
    status = tweet_text    
    status += ("\nLikes:") + str(likes) +"\n"
    status += str(tweet.display_text_range)
    status += StoryUrl
    return status


def send_to_telegram(message): 
    BOT.send_message(chat_id="@ReTweet_channel", text=message, parse_mode=telegram.ParseMode.HTML )  


def read_user_conf():
    with open(CONFIG_FILE, 'r') as userlist:
        out=yaml.load(userlist)
        return out

if __name__ == '__main__':
    users = read_user_conf()
    for user in users:
        print "Tweets/Retweets by @" + user + " in the past 24 hours."
        get_tweets(user)
