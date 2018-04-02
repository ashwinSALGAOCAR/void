# Use an official Python runtime as a parent image.
FROM python:2.7.12

# Create a DIR for our app to sit in.
RUN mkdir /tweetbot

# Set the working directory to /tweetbot
WORKDIR /tweetbot

# Copy the requirements file to the WORKDIR of the Container.
COPY teletweets-req.txt /tweetbot

# Install the needed packages specified in teletweets-req.txt
RUN pip install -r teletweets-req.txt

# Copy the required files to the WORKDIR of the Container.
COPY tele_tweet_channel.py /tweetbot
COPY config.py /tweetbot
COPY users.yaml /tweetbot
	  
# Run tele_tweet_channel.py when the container launches.
CMD ["python", "./tele_tweet_channel.py"]
