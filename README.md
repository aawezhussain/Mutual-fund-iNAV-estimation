# AMFI Mutual Fund NAV Fetcher

A simple Python utility to **fetch and filter mutual fund NAV data from
AMFI (Association of Mutual Funds in India)**.

The tool downloads the official NAV dataset and allows you to **extract
NAV values for specific fund scheme IDs**.

Data source: https://www.amfiindia.com/spages/NAVAll.txt

------------------------------------------------------------------------

# Features

-   Fetch latest NAV data directly from AMFI
-   Parse the AMFI NAV dataset
-   Filter by specific **Scheme Codes (Fund IDs)**
-   Display formatted output
-   Return results as a Python list for further processing

------------------------------------------------------------------------

# Project Structure

    project/
    │
    ├── main.py
    ├── amfi_nav_fetcher.py
    └── README.md

------------------------------------------------------------------------

# Installation

Clone the repository:

    git clone https://github.com/yourusername/amfi-nav-fetcher.git
    cd amfi-nav-fetcher

Install dependencies:

    pip install requests

------------------------------------------------------------------------

# Usage

Run the program:

    python main.py

Example output:

    ================================================================================
    AMFI NAV Data Retrieval
    ================================================================================

    📊 Fetching AMFI NAV data...
    🔍 Parsing NAV data...
    ✅ Total funds in AMFI database: 15000+
    🎯 Filtering for 3 fund(s)...
    ✅ Found 3 fund(s)

    ================================================================================
    Retrieved Fund Data
    ================================================================================
    Fund ID      Fund Name                                      NAV Date     NAV Value
    --------------------------------------------------------------------------------
    118955       HDFC Flexi Cap Fund                            04-Mar-2026      45.23
    118989       Example Fund 2                                 04-Mar-2026      12.34
    122639       Example Fund 3                                 04-Mar-2026      67.89
    ================================================================================

------------------------------------------------------------------------

# Example API Usage

You can use the module inside other Python programs.

``` python
from amfi_nav_fetcher import get_nav_data

funds = {118955, 122639}
data = get_nav_data(funds)

print(data)
```

Example result:

    [
     ['118955', 'HDFC Flexicap Fund...', '04-Mar-2026', '45.23'],
     ['122639', 'Example Fund...', '04-Mar-2026', '67.89']
    ]

------------------------------------------------------------------------

# How It Works

1.  Fetch NAV dataset from AMFI.
2.  Parse semicolon-delimited records.
3.  Extract fund ID, name, NAV date, and NAV value.
4.  Filter results by requested scheme IDs.
5.  Display formatted output.

------------------------------------------------------------------------

# Possible Extensions

Future improvements could include:

-   Intraday NAV estimation
-   Portfolio tracking
-   REST API for NAV data
-   Historical NAV storage
-   Dashboard visualization

Example stack:

-   Python
-   FastAPI
-   PostgreSQL
-   Redis
-   React

------------------------------------------------------------------------

# Data Source

Association of Mutual Funds in India (AMFI)

https://www.amfiindia.com

------------------------------------------------------------------------

# License

MIT License
