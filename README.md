# Personal Expense Tracker 💰📊

## Overview
This project is a **Streamlit dashboard** for visualizing and analyzing personal financial data. It was created as part of the course **968-253 Data Visualization** and uses a dataset from Kaggle.

⚠️ Note: This is an **academic project** for educational purposes only. It is not intended as professional financial advice.

## Features
- 📂 Load and filter expense data by date range and category.
- 📊 Key metrics: total income, expenses, net savings, savings rate.
- 📉 Visualizations:
  - Monthly income vs expenses
  - Expense distribution by category
  - Daily spending patterns
  - Running balance over time
  - Top 10 expense transactions
  - Income sources breakdown
  - Monthly category breakdown
  - Expense heatmap (day × hour)
- 📥 Export filtered data to CSV.

## Tech Stack
- **Python Libraries**: pandas, numpy, matplotlib, seaborn, plotly, streamlit
- **Data Source**: [Kaggle – My Expenses Data](https://www.kaggle.com/datasets/tharunprabu/my-expenses-data)
- **Deployment**: [Render](https://render.com) (see `render.yaml`)

## Project Structure
```
Personal-Expense-Tracker/
├── Personal_Expense_Tracker_Project.py   # Streamlit app
├── expense_data_1.csv                    # Bundled Kaggle dataset
├── requirements.txt
├── render.yaml
└── runtime.txt
```

## Getting Started

### Prerequisites
- Python 3.9

### Installation
```bash
git clone https://github.com/INciD1/Personal-Expense-Tracker.git
cd Personal-Expense-Tracker
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run locally
```bash
streamlit run Personal_Expense_Tracker_Project.py
```
Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Known Limitations
- The dashboard reads a fixed, bundled CSV (`expense_data_1.csv`) — there's no file-upload option to analyze your own data yet.
- Data covers a fixed period (November 2021 – March 2022) since it's a static sample dataset, not live data.

## Possible Improvements
- Add a file-uploader so users can analyze their own expense CSV instead of the bundled sample.
- Add currency selection (dataset is in INR).

## Author
- **Auchukorn Veschapun** (6630611033)
- **Ram Kiatiruangwit** (6630611032)
- **Chanathip Keawklin** (6630611051)

---
