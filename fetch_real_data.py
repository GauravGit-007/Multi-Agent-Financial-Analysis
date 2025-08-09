#!/usr/bin/env python3
"""
fetch_real_data.py - Fixed version

Usage example:
  python fetch_real_data.py --tickers RELIANCE.NS,TCS.NS --start 2025-08-01 --end 2025-08-09 --news_days 5

Dependencies:
  pip install yfinance feedparser vaderSentiment pandas numpy
"""

import argparse
import datetime as dt
import pandas as pd
import numpy as np

def fetch_stock_data(tickers, start, end, interval="1d"):
    """Fetch OHLCV per ticker using yfinance. Returns a concatenated DataFrame."""
    try:
        import yfinance as yf
    except Exception as e:
        raise ImportError("yfinance is required. Install: pip install yfinance") from e

    out = []
    for t in tickers:
        print(f"Fetching stock data for {t} from {start} to {end}...")
        try:
            df = yf.download(t, start=start, end=end, interval=interval, progress=False, threads=True)
        except Exception as e:
            print(f"  Warning: download failed for {t}: {e}")
            continue
        if df is None or df.empty:
            print(f"  No data for {t}")
            continue
        df = df.reset_index()
        # keep only standard columns if present
        cols_map = {}
        if "Open" in df.columns: cols_map["Open"]="Open"
        if "High" in df.columns: cols_map["High"]="High"
        if "Low" in df.columns: cols_map["Low"]="Low"
        if "Close" in df.columns: cols_map["Close"]="Close"
        if "Volume" in df.columns: cols_map["Volume"]="Volume"
        df = df.rename(columns=cols_map)
        # ensure required columns exist
        for c in ["Open","High","Low","Close","Volume"]:
            if c not in df.columns:
                df[c] = np.nan
        df["Company"] = t
        out.append(df[["Date","Company","Open","High","Low","Close","Volume"]])
    if not out:
        return pd.DataFrame(columns=["Date","Company","Open","High","Low","Close","Volume"])
    return pd.concat(out, ignore_index=True)

def fetch_news_rss_for_ticker(ticker, days=7):
    """Fetch recent headlines from Google News RSS for a ticker. Returns list of dicts."""
    try:
        import feedparser
        import urllib.parse as up
    except Exception as e:
        raise ImportError("feedparser is required. Install: pip install feedparser") from e

    q = up.quote_plus(f"{ticker} company")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    parsed = feedparser.parse(url)
    items = []
    cutoff = dt.datetime.utcnow() - dt.timedelta(days=days)
    for e in parsed.entries:
        published = None
        if hasattr(e, "published_parsed") and e.published_parsed:
            published = dt.datetime(*e.published_parsed[:6])
        elif hasattr(e, "updated_parsed") and e.updated_parsed:
            published = dt.datetime(*e.updated_parsed[:6])
        else:
            # if no date, skip (avoids junk)
            continue
        if published < cutoff:
            continue
        headline = getattr(e, "title", None)
        if not headline:
            continue
        items.append({"Date": published.date().isoformat(), "Headline": headline, "Company": ticker})
    return items

def sentiment_label(headlines):
    """Apply VADER sentiment to a list of headline dicts. Returns DataFrame."""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except Exception as e:
        raise ImportError("vaderSentiment is required. Install: pip install vaderSentiment") from e

    if not headlines:
        return pd.DataFrame(columns=["Date","Headline","Company","SentimentLabel","Compound"])

    an = SentimentIntensityAnalyzer()
    rows = []
    for h in headlines:
        txt = h.get("Headline","")
        s = an.polarity_scores(txt)
        comp = s.get("compound", 0.0)
        if comp > 0.05:
            lab = "Positive"
        elif comp < -0.05:
            lab = "Negative"
        else:
            lab = "Neutral"
        rows.append({
            "Date": h.get("Date"),
            "Headline": txt,
            "Company": h.get("Company"),
            "SentimentLabel": lab,
            "Compound": comp
        })
    return pd.DataFrame(rows)

def simple_economic_proxy(start, end):
    """Return a clean single-row DataFrame with hardcoded Indian macro values."""
    latest_date = pd.to_datetime(end).date().isoformat()
    data = [{
        "Date": latest_date,
        "Inflation Rate": 0.021,     # 2.1%
        "Unemployment Rate": 0.056,  # 5.6%
        "GDP Growth": 0.068          # 6.8%
    }]
    return pd.DataFrame(data)

def parse_args():
    p = argparse.ArgumentParser(description="Fetch real stock + news + economic data (minimal).")
    p.add_argument("--tickers", required=True, help="Comma-separated tickers e.g. AAPL,TSLA,RELIANCE.NS")
    p.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    p.add_argument("--end", required=True, help="End date YYYY-MM-DD (exclusive for yfinance)")
    p.add_argument("--news_days", type=int, default=7, help="How many past days of news to fetch per ticker")
    return p.parse_args()

def main():
    args = parse_args()
    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
    start = args.start
    end = args.end
    news_days = args.news_days

    # Stock data
    stock_df = fetch_stock_data(tickers, start, end)
    if stock_df.empty:
        print("No stock data fetched. Check tickers or date range.")

    # News data
    all_news = []
    for t in tickers:
        try:
            items = fetch_news_rss_for_ticker(t, days=news_days)
            all_news.extend(items)
        except Exception as e:
            print(f"  Warning: news fetch failed for {t}: {e}")
    news_df = sentiment_label(all_news)

    # Economic data (hardcoded clean proxy)
    econ_df = simple_economic_proxy(start, end)

    # Save outputs
    stock_df.to_csv("stock_prices.csv", index=False)
    if not news_df.empty:
        news_df.to_csv("news_articles.csv", index=False)
    else:
        # write an empty but well-formed CSV
        pd.DataFrame(columns=["Date","Headline","Company","SentimentLabel","Compound"]).to_csv("news_articles.csv", index=False)
    econ_df.to_csv("economic_indicators.csv", index=False)

    print("Saved: stock_prices.csv, news_articles.csv, economic_indicators.csv")

if __name__ == "__main__":
    main()
