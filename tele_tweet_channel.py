#code to fetch a particular users Tweets in the last 24 hours and liking it if not liked before.
import tweepy, datetime, time, pytz, yaml, telegram, requests, urllib3
from config import access_key, access_secret, consumer_key, consumer_secret, telegram_PIN

#Fetch the Twitter keys and secrets for the script ti access Twitter.

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)

#Fetch the Telegram token for the script to access Telegram.

bot = telegram.Bot(token=telegram_PIN)


#My Details.
#user = api.me()

#print('Name: ' + user.name)
#print('Location: ' + user.location)
#print('Friends: ' + str(user.friends_count))



def get_tweets(api, username):
#    request = requests.get(url, stream=True)
#    print request
    page = 1
    deadend = False
    max_tweets = 10
    http = urllib3.PoolManager()
    
    while True:

        for tweet in tweepy.Cursor(api.user_timeline, username, page = page, include_entities = True, tweet_mode='extended').items():
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
                
#                print utc
#                print ist
#                print utc_date
#                print ist_date
                #Fetching the Users Twitter Handle. Ex: @ashwinSALGAOCAR
                #and the Tweet ID

                tw_handle = '@' + api.get_user(tweet.user.id_str).screen_name
                #If the Tweet is a ReTweet, it gets truncated, hence we print the tweet._json
                if 'retweeted_status' in tweet._json:
                     retweet_text = tw_handle +' retweeted @' + api.get_user(tweet.retweeted_status.user.id_str).screen_name          #Appends RT @ to the Retweet.

                     #If the tweet is not Liked/Favorited, then only Like/Favorite the tweet.
#                     try:
#                         if not tweet.favorite():
#                             tweet.favorite()
#                             print('You Liked the Retweet')
#                     except tweepy.TweepError as e:
#                         print('You have already Liked/Favorited the Retweet')

                     if tweet.retweeted_status.entities['urls']:
                         for url in tweet.retweeted_status.entities['urls']:
                             StoryUrl = "\n\nLike/Retweet/Comment at https://twitter.com/"+api.get_user(tweet.retweeted_status.user.id_str).screen_name+"/status/"+tweet.retweeted_status.id_str+"\n\nOr visit the link in the Retweet directly via: "+url['expanded_url']
                     else:
                         StoryUrl ="\n\nLike/Retweet/Comment at https://twitter.com/"+api.get_user(tweet.retweeted_status.user.id_str).screen_name+"/status/"+tweet.retweeted_status.id_str+'\n\nNo Urls in this Retweet.'
 
                     RT_likes = tweet.retweeted_status.favorite_count
                     status = ist_date.strftime(fmt) +"\n"+ (retweet_text +"\n"+ tweet._json['retweeted_status']['full_text']) + ("\nLikes: ") +str(RT_likes) +"\n"+str(tweet.display_text_range)+ StoryUrl
                    
                     bot.send_message(chat_id="@ReTweet_channel", text=status, parse_mode=telegram.ParseMode.HTML)

                #Else if it is a Tweet, simply paste the full text.
                else:

                     #If the tweet is not Liked/Favorited, then only Like/Favorite the tweet.
#                     try:
#                         if not tweet.favorite():
#                             tweet.favorite()
#                             print('You Liked the Tweet') 
#                     except tweepy.TweepError as e:
#                         print('You have already Liked/Favorited the Tweet')
                    if tweet.entities['urls']:
                         for url in tweet.entities['urls']:
                             StoryUrl = "\n\nLike/Retweet/Comment at https://twitter.com/"+api.get_user(tweet.user.id_str).screen_name+"/status/"+tweet.id_str+"\n\nOr visit the link in the Tweet directly via: "+url['expanded_url']
                    else:
                        StoryUrl = "\n\nLike/Retweet/Comment at https://twitter.com/"+api.get_user(tweet.user.id_str).screen_name+"/status/"+tweet.id_str+'\n\nNo Urls in this Tweet.'

                    T_likes = tweet.favorite_count
                    status = ist_date.strftime(fmt) +"\n"+ (tw_handle +"\n"+ tweet.full_text)+ ("\nLikes:")+str(T_likes) +"\n"+ str(tweet.display_text_range)+ StoryUrl

                    bot.send_message(chat_id="@ReTweet_channel", text=status, parse_mode=telegram.ParseMode.HTML)
            else:
                deadend = True
                return
        if not deadend:
            page+=1
            time.sleep(5)


with open('users.yaml','r') as userlist:
    out=yaml.load(userlist)
    for data in out:
        print "Tweets/Retweets by @" +data+ " in the past 24 hours."
        get_tweets(api, data)
