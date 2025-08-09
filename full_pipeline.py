# full_pipeline.py
import pandas as pd

def run_pipeline():
    # Read CSV files
    stocks = pd.read_csv("stock_prices.csv")
    news = pd.read_csv("news_articles.csv")
    econ = pd.read_csv("economic_indicators.csv")

    # Ensure date format consistency
    stocks["Date"] = pd.to_datetime(stocks["Date"])
    news["Date"] = pd.to_datetime(news["Date"])
    econ["Date"] = pd.to_datetime(econ["Date"])

    # Merge stock + news on Date & Company
    merged = pd.merge(stocks, news, on=["Date", "Company"], how="left")

    # Merge with economic indicators (on Date only)
    merged = pd.merge(merged, econ, on="Date", how="left")

    # Save combined file
    merged.to_csv("final_combined.csv", index=False)
    merged.to_excel("final_combined.xlsx", index=False)

    print("✅ Merged file saved as final_combined.csv and final_combined.xlsx")

if __name__ == "__main__":
    run_pipeline()
