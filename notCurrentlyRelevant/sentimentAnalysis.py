# %%
# gather tweets about bitcoin at different time to plot sentiment overtime
from twitterCredentials import Access_token, Access_token_Secret, API_key as consumerKey, API_key_secret as consumerSecret, Bearer_token
import tweepy
from textblob import TextBlob
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

# %%
client = tweepy.Client(
    bearer_token=Bearer_token,
    consumer_key=consumerKey,
    consumer_secret=consumerSecret,
    access_token=Access_token,
    access_token_secret=Access_token_Secret,
    wait_on_rate_limit=True)

# %%
