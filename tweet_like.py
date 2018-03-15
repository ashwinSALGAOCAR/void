#code to fetch a particular users Tweets in the last 24 hours and liking it if not liked before.
import tweepy, datetime, time, pytz
from config import access_key, access_secret, consumer_key, consumer_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)

#My Details.
#user = api.me()

#print('Name: ' + user.name)
#print('Location: ' + user.location)
#print('Friends: ' + str(user.friends_count))

#Set Timezone variables to store Twitter's UTC Time and converting it to IST Time.
utc = pytz.timezone('UTC')
ist = pytz.timezone('Asia/Calcutta')


def get_tweets(api, username):
    page = 1
    deadend = False
    max_tweets = 10

    while True:

        for tweet in tweepy.Cursor(api.user_timeline, username, page = page, tweet_mode='extended').items():
            if (datetime.datetime.now() - tweet.created_at).days <= 1:
                #Do processing here:
                utc_date=utc.localize(tweet.created_at)
                ist_date  = utc_date.astimezone(ist)
                #24 hour Format.
                #    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
                #12 hour Format.
                fmt = '%Y-%m-%d %I:%M %p %Z'
                print ist_date.strftime(fmt)
                #Fetching the Users Twitter Handle. Ex: @ashwinSALGAOCAR
                tw_handle = '@' + api.get_user(tweet.user.id_str).screen_name
                #If the Tweet is a ReTweet, it gets truncated, hence we print the tweet._json
                if 'retweeted_status' in tweet._json:
                     retweet_text = tw_handle +' retweeted @' + api.get_user(tweet.retweeted_status.user.id_str).screen_name          #Appends RT @ to the Retweet.

                     RT_likes = tweet.retweeted_status.favorite_count
                     #If the tweet is not Liked/Favorited, then only Like/Favorite the tweet.
                     try:
                         if not tweet.favorite():
                             tweet.favorite()
#                         print('You Liked the Retweet')
                     except tweepy.TweepError as e:
                         print('You have already Liked/Favorited the Retweet')

                     print(retweet_text +"\n"+ tweet._json['retweeted_status']['full_text'])
                     print "Likes:" +str(RT_likes)
                     print(tweet.display_text_range)
                     print("\n")

                #Else if it is a Tweet, simply paste the full text.
                else:
                     T_likes = tweet.favorite_count
                     #If the tweet is not Liked/Favorited, then only Like/Favorite the tweet.
                     try:
                         if not tweet.favorite():
                             tweet.favorite()
#                             print('You Liked the Tweet')
                     except tweepy.TweepError as e:
                         print('You have already Liked/Favorited the Tweet')

                     print tw_handle +"\n"+ tweet.full_text
                     print "Likes:" +str(T_likes)
                     print (tweet.display_text_range)
                     print "\n"

            else:
                deadend = True
                return
        if not deadend:
            page+=1
            time.sleep(500)


get_tweets(api, "prankz25")
