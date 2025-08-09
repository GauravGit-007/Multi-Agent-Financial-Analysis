import subprocess
import sys
import os

def run_or_exit(command):
    """Run a shell command, exit if it fails."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Step failed: {command}")
        sys.exit(1)

if __name__ == "__main__":
    # 1. Fetch real data (stocks, news, economic indicators)
    run_or_exit("python fetch_real_data.py --tickers RELIANCE.NS,TCS.NS --start 2025-08-01 --end 2025-08-09 --news_days 7")

    # (Optional: Clean stock data if needed)
    # run_or_exit("python clean_stock_data.py")
    # run_or_exit("python fix_stock_format.py")

    # 2. Merge all data
    run_or_exit("python full_pipeline.py")

    # 3. Run recommendation agent
    run_or_exit("python decision_agent.py")

    print("\n✅ All agents executed successfully!")
    print("Outputs: final_combined.csv, final_combined.xlsx, recommendations.csv")
