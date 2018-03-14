from datetime import datetime
import tweepy
import pytz
from config import consumer_key, consumer_secret, access_key, access_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)


#Set Timezone variables to store Twitter's UTC Time and converting it to IST Time.
utc = pytz.timezone('UTC')
ist = pytz.timezone('Asia/Calcutta')

max_tweets = 10
for tweet in tweepy.Cursor(api.search,
                           q="#Crypto",
			   tweet_mode='extended'
                           ).items(max_tweets):


    utc_date=utc.localize(tweet.created_at)
    ist_date  = utc_date.astimezone(ist)
#24 hour Format.
#    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
#12 hour Format.
    fmt = '%Y-%m-%d %I:%M %p %Z'
    print ist_date.strftime(fmt)

#If the Tweet is a ReTweet, it gets truncated, hence we print the tweet._json

    if 'retweeted_status' in tweet._json:
            retweet_text = 'RT @' + api.get_user(tweet.retweeted_status.user.id_str).screen_name          #Appends RT @ to the Retweet.
            print(retweet_text +"\n"+ tweet._json['retweeted_status']['full_text'])

#Else if it is a Tweet, simply paste the full text.
    else:
            print(tweet.full_text)

    
#    print tweet.full_text.encode(encoding='UTF-8',errors='strict')
#    print tweet.full_text

    print (tweet.display_text_range)
    print "\n"
