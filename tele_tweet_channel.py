#code to fetch a particular users Tweets in the last 24 hours and liking it if not liked before.
import tweepy, datetime, time, pytz, yaml, telegram, requests, urllib3
from config import access_key, access_secret, consumer_key, consumer_secret, telegram_PIN

#Fetch the Twitter keys and secrets for the script ti access Twitter.

AUTH = tweepy.OAuthHandler(consumer_key, consumer_secret)
AUTH.set_access_token(access_key, access_secret)

API = tweepy.API(auth)

#Fetch the Telegram token for the script to access Telegram.

BOT = telegram.Bot(token=telegram_PIN)


#My Details.
#user = api.me()

#print('Name: ' + user.name)
#print('Location: ' + user.location)
#print('Friends: ' + str(user.friends_count))

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
            #Do processing here:
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
                #If the Tweet is a ReTweet, it gets truncated, hence we print the tweet._json
                no_url = '\n\nNo Urls in this Tweet.'
                message = "\n\nLike/Retweet/Comment at https://twitter.com/{0}/status/{1}"
                visit_link = "\n\nOr visit the link in the {0} directly via: "

                if 'retweeted_status' in tweet._json:

                    screen_name, tweet_id = get_tweet_details(tweet.retweeted_status)

                    retweet_text = tw_handle +' retweeted @' + screen_name          #Appends RT @ to the Retweet.

                    if tweet.retweeted_status.entities['urls']:
                        for url in tweet.retweeted_status.entities['urls']:
                            StoryUrl = message + visit_link.format("Retweet") + url['expanded_url']
                    else:
                        StoryUrl = message + no_url

                    likes = tweet.retweeted_status.favorite_count

                #Else if it is a Tweet, simply paste the full text.
                else:

                    screen_name = API.get_user(tweet.user.id_str).screen_name
                    tweet_id = tweet.id_str

                    if tweet.entities['urls']:
                         for url in tweet.entities['urls']:
                             StoryUrl = message + visit_link.format("Tweet") + url['expanded_url']
                    else:
                        StoryUrl = message + no_url

                    likes = tweet.favorite_count

                status = make_status(likes, StoryUrl)
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


def make_status(tw_handle, full_text, likes, tweet, StoryUrl):

    status = ist_date.strftime(fmt)

    tweet_text = "\n" + tw_handle

    if tweet_type == 'retweet':
        tweet_text += "\n"+ tweet._json['retweeted_status']['full_text']
    else:
        tweet_text += "\n"+ tweet.full_text
        
    status += tweet_text    
    status += ("\nLikes:") + str(likes) +"\n"
    status += str(tweet.display_text_range)
    status += StoryUrl

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
