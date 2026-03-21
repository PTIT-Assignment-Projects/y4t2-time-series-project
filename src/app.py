import streamlit as st
import pandas as pd
import os
import numpy as np

# Try to disable Arrow-based string inference in newer pandas versions 
# to avoid LargeUtf8 compatibility issues with Streamlit 1.19.0
try:
    pd.set_option("future.no_silent_downcasting", True)
except:
    pass


st.set_page_config(page_title="FX-BOT Results", layout="wide")
st.title("FX-BOT: Currency Pair Analysis Results")

# Path to local data directory
data_dir = "local_data/"

# Show available data files
data_files = os.listdir(data_dir) if os.path.exists(data_dir) else []

if not data_files:
    st.warning("No results found. Please run the data pipeline first.")
else:
    st.sidebar.header("Available Data Files")
    for file in data_files:
        st.sidebar.write(file)

    # Show model predictions and best currency pair to invest in
    tickers_path = os.path.join(data_dir, "tickers_df.parquet")
    if os.path.exists(tickers_path):
        df = pd.read_parquet(tickers_path)
        st.subheader("Currency Pairs: Model Predictions and Ranks")
        # Always try to use XGBoost prediction columns if available
        pred_col = None
        prob_col = None
        rank_col = None
        if 'pred_xgboost_1h_best' in df.columns:
            pred_col = 'pred_xgboost_1h_best'
        if 'prob_pred_xgboost_1h_best' in df.columns:
            prob_col = 'prob_pred_xgboost_1h_best'
        if 'pred_xgboost_1h_best_rank' in df.columns:
            rank_col = 'pred_xgboost_1h_best_rank'
        # Fallback to auto-detect if not found
        if not pred_col or not rank_col:
            for col in df.columns:
                if not rank_col and col.endswith('_rank'):
                    rank_col = col
                if not pred_col and (col.startswith('pred') or col.startswith('y_pred') or col.startswith('class')):
                    pred_col = col
        # If still not found, fallback to default names
        if not rank_col:
            rank_col = 'pred_class1_rank' if 'pred_class1_rank' in df.columns else df.columns[-1]
        if not pred_col:
            pred_col = 'pred_class1' if 'pred_class1' in df.columns else df.columns[-2]

        # Filter for each date and show top/bottom 3 predictions per day
        if 'Date' in df.columns:
            st.write(f"### Forex Currency Pairs Daily Predictions (1-hour future growth)")
            def highlight_buy(val):
                if isinstance(val, (int, float)) and val >= 0.5:
                    return 'background-color: #d4f7d4'  # light green for buy
                elif isinstance(val, (int, float)):
                    return 'background-color: #f7d4d4'  # light red for sell
                return ''

            for date in sorted(df['Date'].unique()):
                df_day = df[df['Date'] == date].copy()
                # Format date for section header to YYYY-MM-DD only
                date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
                st.markdown(f"#### {date_str}")
                # Find probability column
                prob_col = None
                for col in df_day.columns:
                    if 'prob' in col or 'proba' in col:
                        prob_col = col
                        break
                # Show all model predictions (both buy/sell) so actual growth can be compared
                if pred_col in df_day.columns:
                    growth = df_day.copy()
                    
                    if not growth.empty:
                        # Identify columns for display and their clean names
                        # Use a dictionary to avoid duplicates
                        cols_to_show = {"Ticker": "Ticker"}
                        if "DateTime" in growth.columns:
                            cols_to_show["DateTime"] = "Hour"
                        if prob_col and prob_col in growth.columns:
                            cols_to_show[prob_col] = "Probability"
                        actual_growth_col = None
                        if "growth_future_1h" in growth.columns:
                            actual_growth_col = "growth_future_1h"
                        elif "growth_future_4h" in growth.columns:
                            actual_growth_col = "growth_future_4h"
                        elif "is_positive_growth_1h_future" in growth.columns:
                            actual_growth_col = "is_positive_growth_1h_future"

                        if actual_growth_col:
                            cols_to_show[actual_growth_col] = "Actual_Growth"
                        if pred_col in growth.columns and pred_col not in cols_to_show:
                            cols_to_show[pred_col] = "Signal"
                        
                        # Select and rename
                        display_df = growth[list(cols_to_show.keys())].copy()
                        display_df.columns = [cols_to_show[c] for c in display_df.columns]

                        if "Signal" in display_df.columns:
                            display_df["Signal"] = display_df["Signal"].astype(int)
                        
                        if "Actual_Growth" in display_df.columns and actual_growth_col in ["growth_future_1h", "growth_future_4h"]:
                            display_df["Actual_Growth"] = ((display_df["Actual_Growth"] - 1.0) * 100).round(4)

                        if "Probability" in display_df.columns:
                            display_df = display_df.sort_values("Probability", ascending=False)
                        
                        display_df = display_df.reset_index(drop=True)
                        
                        # Aggressive cleaning to bypass Arrow LargeUtf8 issues in Streamlit 1.19.0
                        data_as_list = display_df.values.tolist()
                        clean_growth = pd.DataFrame(data_as_list, columns=display_df.columns.tolist())
                        
                        for col in clean_growth.columns:
                            clean_growth[col] = clean_growth[col].astype(object)

                        st.dataframe(clean_growth)
                        st.caption('Showing all model signals (Signal: 1 = BUY, 0 = SELL).')
                    else:
                        st.info(f'No qualifying predictions found for this day. (Checked column: {pred_col})')
        else:
            st.warning("No 'Date' column found in tickers_df.parquet.")
    else:
        st.info("tickers_df.parquet not found.")


st.markdown("---")
st.caption("FX-BOT Streamlit UI | Results Viewer")