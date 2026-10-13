import pandas as pd
import matplotlib.pyplot as plt

watchlist_df = pd.read_csv("watchlist.csv") # 파이썬이 알아서 정수로 읽어버림.
watchlist_df = pd.read_csv("watchlist.csv", dtype={"code": str}) # dtype으로 str로 읽어라.
print(watchlist_df["code"].tolist())
print(dict(zip(watchlist_df["code"], watchlist_df["name"])))