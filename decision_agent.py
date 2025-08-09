# decision_agent.py
"""
Decision Agent for Multi-Agent Financial Analysis System

Reads final_combined.csv (produced by full_pipeline.py) and generates
BUY / SELL / HOLD recommendations based on sentiment + technical trend.
"""

import pandas as pd


class DecisionAgent:
    def __init__(self, input_file="final_combined.csv", output_file="recommendations.csv"):
        self.input_file = input_file
        self.output_file = output_file

    def generate_recommendations(self):
        # Load merged dataset
        df = pd.read_csv(self.input_file)

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])

        recommendations = []

        for company in df["Company"].dropna().unique():
            comp_df = df[df["Company"] == company].copy()
            # Calculate 3-day moving average of Close price
            comp_df["MA3"] = comp_df["Close"].rolling(window=3).mean()

            for _, row in comp_df.iterrows():
                signal = "HOLD"
                reason = "Neutral or no strong signal"

                sentiment = row.get("SentimentLabel", None)
                ma3 = row.get("MA3", None)

                # Apply simple rule-based strategy
                if pd.notna(sentiment) and pd.notna(ma3):
                    if sentiment == "Positive" and row["Close"] > ma3:
                        signal = "BUY"
                        reason = "Positive sentiment + price above short-term trend"
                    elif sentiment == "Negative" and row["Close"] < ma3:
                        signal = "SELL"
                        reason = "Negative sentiment + price below short-term trend"

                recommendations.append({
                    "Date": row["Date"].date() if pd.notna(row["Date"]) else None,
                    "Company": company,
                    "Close": row["Close"],
                    "Sentiment": sentiment if sentiment else "None",
                    "Signal": signal,
                    "Reason": reason
                })

        # Save recommendations
        recs_df = pd.DataFrame(recommendations)
        recs_df.to_csv(self.output_file, index=False)
        print(f"✅ Recommendations saved to {self.output_file}")


if __name__ == "__main__":
    agent = DecisionAgent()
    agent.generate_recommendations()
