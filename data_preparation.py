import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def cleanPriceValues(df):
    df['price'] = df['price'].apply(lambda x: float(x[1:].replace(',','').replace("$","")))
    df['extra_people'] = df['extra_people'].apply(lambda x: float(x[1:].replace(',','').replace("$","")))
    return df

def addMaxPrice(df):
    df["max_price"] = np.add(df['price'], (np.subtract(df['accommodates'],df['guests_included']) * df['extra_people']))
    return df

def addPopularity(df):
    df["popularity"] = df['number_of_reviews_ltm'] * (df['review_scores_rating']/100)
    return df

def addEarningScore(df):
    df["earnings_score"] = df["number_of_reviews_ltm"] * df["max_price"]    
    return df

def cleanData(df):
    df = df[df['price'] > 0]
    df = df[df['availability_365'] > 0]
    df = df[df['accommodates'] >= df['guests_included']]
    df.dropna()
    return df

df_reviews = pd.read_csv('reviews_cph.csv')
df_listings = pd.read_csv('listings_cph.csv')

df_listings =  cleanPriceValues(df_listings)
df_listings = cleanData(df_listings)


df_multilistings = df_listings[["host_id", "host_name","id"]]
df_multilistings = df_multilistings.groupby(["host_id", "host_name"]).count().reset_index()
df_multilistings = df_multilistings.rename(index=str, columns={"id": "listing_count"})

df_multilistings.to_csv("multilistings.csv", index=False)

df_reviews.date = pd.to_datetime(df_reviews.date, format='%Y-%m-%d')

df_yearly_review_count = df_reviews.groupby(df_reviews.date.dt.year).count()[["id"]]
df_yearly_review_count['year'] = df_yearly_review_count.index


df_monthly_review_count  = df_reviews.groupby([df_reviews.date.dt.year, df_reviews.date.dt.month]).count()[["id"]]
df_monthly_review_count['month'] = df_monthly_review_count.index
df_monthly_review_count = df_monthly_review_count.rename(index=str, columns={"id": "review_count"})
df_monthly_review_count['month'] = df_monthly_review_count['month'].astype(str)
df_monthly_review_count.to_csv("monthly_review_count.csv", index=False)

df_yearly_review_count = df_yearly_review_count.rename(index=str, columns={"id": "review_count"})
df_yearly_review_count.to_csv("yearly_review_count.csv", index=False)

df_earnings_per_listing = df_listings[["host_id", "host_name", "id", "number_of_reviews_ltm", "price", "guests_included","extra_people", "accommodates", "review_scores_rating", "number_of_reviews"]]

df_earnings_per_host = df_earnings_per_listing.copy()
df_earnings_per_host = addMaxPrice(df_earnings_per_host)
df_earnings_per_host = addPopularity(df_earnings_per_host)
df_earnings_per_host = addEarningScore(df_earnings_per_host)
df_earnings_per_host = df_earnings_per_host.dropna()

df_earnings_per_listing = addMaxPrice(df_earnings_per_listing)
df_earnings_per_listing = addPopularity(df_earnings_per_listing)
df_earnings_per_listing = addEarningScore(df_earnings_per_listing)
df_earnings_per_listing = df_earnings_per_listing.dropna()

df_earnings_per_listing = df_earnings_per_listing [["id", "host_id","earnings_score", "max_price", "popularity", "number_of_reviews_ltm"]]
df_earnings_per_listing["earnings_score"] = (df_earnings_per_listing["earnings_score"]-df_earnings_per_listing["earnings_score"].min())/(df_earnings_per_listing["earnings_score"].max()-df_earnings_per_listing["earnings_score"].min())
df_earnings_per_listing["popularity"] = (df_earnings_per_listing["popularity"]-df_earnings_per_listing["popularity"].min())/(df_earnings_per_listing["popularity"].max()-df_earnings_per_listing["popularity"].min())
 
df_earnings_per_listing.to_csv("earnings_per_listing.csv", index=False)

df_earnings_per_host = df_earnings_per_host.groupby("host_id").agg({'earnings_score': 'sum', 
                         'max_price':'sum', 
                         'number_of_reviews_ltm':'sum', 
                         'popularity': 'mean',
                         'id':'count',
                         'host_name': 'unique'})

   
df_earnings_per_host["earnings_score"] = (df_earnings_per_host["earnings_score"]-df_earnings_per_host["earnings_score"].min())/(df_earnings_per_host["earnings_score"].max()-df_earnings_per_host["earnings_score"].min())
df_earnings_per_host["popularity"] = (df_earnings_per_host["popularity"]-df_earnings_per_host["popularity"].min())/(df_earnings_per_host["popularity"].max()-df_earnings_per_host["popularity"].min())

df_earnings_per_host = df_earnings_per_host.rename(index=str, columns={'id':'listing_count'})

df_earnings_per_host["host_name"] = df_earnings_per_host["host_name"].apply(lambda x: x[0]) 

df_earnings_per_host["host_id"] = df_earnings_per_host.index

df_earnings_per_host.to_csv("earnings_per_host.csv", index=False)



