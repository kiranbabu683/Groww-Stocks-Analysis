# Groww Stocks Analysis: What 658 Listed Companies Tell Us

An end-to-end data analytics project: scraping Indian stock data from [groww.in](https://groww.in), cleaning it, analysing it, and presenting the findings in an Excel dashboard and a presentation.

**Workflow:** Website selection → Data collection → Data understanding → Data cleaning → Exploratory analysis → Visualisation → Business insights → Presentation

---

## Project Summary

- **Collected:** 800 stock pages, a random sample of 5,987 listed instruments (about 13%)
- **Cleaned:** 800 rows, 46 columns; 658 real, actively traded companies with fundamentals marked as analysis-ready
- **Analysed:** company size, industry, valuation, profitability, ownership and distance from the 52-week high
- **Delivered:** Excel dashboard with filters, EDA notebook with charts, and a 7-slide presentation

## Key Findings

- **Value is concentrated.** 42 large caps (6% of companies) hold about 84% of total market value. Two in three companies are micro caps holding under 1%.
- **Quality rises with size.** Profitable companies go from 67% (micro) to 98% (large). Dividend payers go from 12% to 76%. Institutional holding goes from about 1% to 32%.
- **Risk sits in small names.** 145 of the 165 loss-making companies are micro caps.
- **IT dominates.** Information Technology is about 35% of total market value.
- **Most stocks are far below their highs.** 53% trade more than 30% below their 52-week high.
- **A simple quality screen** (ROE above 15%, debt-to-equity below 0.5, profitable, P/E below industry P/E, market cap of at least ₹500 Cr) is passed by 31 companies.

> Learning project based on a one-day snapshot. Not investment advice.

## Repository Structure

```
groww-stocks-analysis/
├── README.md
├── 1_scraping/
│   ├── Regex_Project.ipynb        # scraper notebook (links + 800 stock pages)
│   └── industry_fix.py            # reads industry names from hidden page data
├── 2_data/
│   ├── groww_stock_urls.csv       # 5,987 stock links
│   ├── groww_raw_stocks.csv       # raw scrape, 800 rows
│   ├── groww_raw_stocks_industry.csv   # raw data + Industry
│   ├── groww_cleaned_stocks.csv   # final cleaned data (800 rows, 46 columns)
│   └── Groww_Cleaned_Data.xlsx    # cleaned data, data dictionary, cleaning log
├── 3_cleaning/
│   └── Groww_Cleaning.ipynb
├── 4_eda/
│   └── Groww_EDA.ipynb
├── 5_dashboard/
│   └── Groww_Dashboard.xlsx
└── 6_presentation/
    └── Groww_Stocks_Analysis.pptx
```

## How the Pieces Connect

| Step | File | Reads | Produces |
|---|---|---|---|
| 1. Scrape | `Regex_Project.ipynb` | groww.in | `groww_stock_urls.csv`, `groww_raw_stocks.csv` |
| 2. Add industry | `industry_fix.py` | `groww_raw_stocks.csv` | `groww_raw_stocks_industry.csv` |
| 3. Clean | `Groww_Cleaning.ipynb` | `groww_raw_stocks_industry.csv` | `groww_cleaned_stocks.csv`, `Groww_Cleaned_Data.xlsx` |
| 4. Explore | `Groww_EDA.ipynb` | `groww_cleaned_stocks.csv` | charts and findings |
| 5. Dashboard | `Groww_Dashboard.xlsx` | the 658 analysis-ready companies | KPIs and 8 charts with filters |
| 6. Present | `.pptx` | findings from steps 4 and 5 | 7 slides |

## Data Collection

- **Tools:** `requests`, `BeautifulSoup` and regex
- **Method:** walk the A–Z stock lists to collect every stock link, take a random sample (seed 42), then read each stock page
- **Fields:** price, day and 52-week range, market cap, ROE, P/E, EPS, P/B, dividend yield, debt-to-equity, shareholding (promoters, DII, FII, public), CEO, founded year and more
- **Industry** is not visible text on the page, so it is read from the page's hidden JSON data (`__NEXT_DATA__`). It was found for 798 of 800 stocks.
- The scraper waits 1 to 2 seconds between pages and saves progress every 25 stocks, so it can resume.

## Data Cleaning (summary)

The full list is in the **Cleaning_Log** sheet of `Groww_Cleaned_Data.xlsx`.

| Issue | Rows | What I did |
|---|---|---|
| Fake 52-week low and high (both exactly 52.0, a scraper artefact) | 108 | Set to blank |
| ETFs mixed with company shares | 57 | Flagged `Instrument_Type = ETF` |
| Price of 0 (suspended or delisted) | 85 | Flagged `Inactive`, price set to blank |
| Blank DII / FII / promoter holding | - | Filled with 0, after checking each row adds up to 100% |
| Missing financial ratios | - | Left blank, not guessed |
| Extreme ROE, P/E or dividend yield | - | Flagged, not deleted |

New columns include daily price change, distance from 52-week high, market-cap size band (Micro, Small, Mid, Large), company age, institutional holding, profitable and pays-dividend flags. Every column is described in the **Data_Dictionary** sheet.

## Dashboard

`Groww_Dashboard.xlsx` has:
- **Filters:** Size and Listing drop-downs
- **8 KPI cards:** companies, total market cap, % profitable, % paying dividends, average P/E, promoter holding, institutional holding, % more than 30% below the 52-week high
- **8 charts:** companies by size, market-cap share, top industries, P/E versus industry P/E, profitability and dividends, ROE, shareholding mix, distance from the 52-week high
- **Sheets:** Dashboard, Insights, Analysis, Data, Quality Screen

All KPIs and charts are driven by formulas, so they update when a filter changes.

## How to Run

1. Install the libraries:
   ```
   pip install requests beautifulsoup4 pandas numpy matplotlib seaborn openpyxl
   ```
2. Put the files of a step in the same folder as its notebook.
3. Run in order: scraper notebook → `industry_fix.py` → `Groww_Cleaning.ipynb` → `Groww_EDA.ipynb`.
4. To add industry names after scraping:
   ```python
   from industry_fix import add_industry
   df = add_industry("groww_raw_stocks.csv")
   ```
   This writes `groww_raw_stocks_industry.csv`, which the cleaning notebook reads.

Scraping 800 pages takes roughly 30 to 40 minutes.

## Limitations

- One-day snapshot, with no price history or returns
- Random sample of about 13% of listed instruments
- Market-cap bands are approximate, not the official SEBI ranking
- "No NSE symbol" is assumed to mean mostly BSE-only listings
- P/E and ROE for micro caps can be extreme

## Responsible Use

Data is publicly visible on groww.in and was collected slowly for learning purposes. Check a website's terms and robots.txt before scraping, and keep requests polite. Nothing here is financial advice.

## Skills Demonstrated

Python | Web scraping (requests, BeautifulSoup, regex) | Data cleaning (pandas) | Exploratory data analysis | Excel dashboarding | Business insights | Documentation

## Author

**[Kiranbabu Kummari]**
[LinkedIn](www.linkedin.com/in/kiran-babu-kummari-163b69317) | Project completed at Innomatics Research Labs
