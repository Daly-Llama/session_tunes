# Session Tunes

Exploratory analysis of traditional Irish tune data scraped from [TheSession.org](https://thesession.org).

## Overview

This project asks a simple question: **what makes a traditional Irish tune popular?**

TheSession.org is a community site where traditional Irish musicians share sheet music, record tune sets, and catalog recordings. It hosts data on over 22,000 tunes, and the site's social features — tunebooks, sets, recordings — leave a measurable trace of which tunes are widely known and played.

This project scrapes that data, builds a dataset, and uses exploratory analysis, hypothesis testing, and regression to understand what drives tune popularity.

## Repository Contents

| File | Description |
|---|---|
| `session_tunes.py` | Web scraper that collects tune metadata from TheSession.org |
| `tunes.json` | Dataset of ~22,000 tunes built by running the scraper |
| `SessionTunes.ipynb` | Analysis notebook: EDA, correlation analysis, hypothesis testing, regression |

## Dataset

Each record in `tunes.json` represents one tune and contains the following variables:

| Variable | Description |
|---|---|
| `name` | The tune's primary name on TheSession.org |
| `aliases` | Other names the tune is known by |
| `type` | Genre (reel, jig, hornpipe, etc.) |
| `tabs` | Number of sheet music submissions on the site |
| `recordings` | Number of times the tune appears in a recorded album |
| `collections` | Number of tune collections the tune belongs to |
| `sets` | Number of sets the tune has been added to |
| `books` | Number of users who have saved the tune to their tunebook |

The `books` variable is used as the primary proxy for tune popularity throughout the analysis.

## Analysis

The notebook covers four areas:

**Data Exploration** — Descriptive statistics, histograms, and boxplots for each key variable. Identifies the heavily right-skewed nature of most variables and handles two data errors in the `books` column caused by the scraper misreading tune names containing numbers.

**Correlation Analysis** — Scatter plots and Pearson/Spearman correlations between popularity-related variables. Key finding: `books` and `sets` are strongly correlated (Pearson = 0.94), and `tabs` and `recordings` show a moderate positive relationship (Pearson = 0.70).

**Hypothesis Test** — A permutation test of whether jigs and reels have significantly higher tunebook save counts than other tune types. The difference is statistically significant across all sample sizes tested.

**Regression** — A simple OLS regression of `books` on `tabs`. The `tabs` variable explains approximately 41% of the variance in tune popularity.

## Running the Scraper

To rebuild `tunes.json` from scratch, run `session_tunes.py`. The scraper iterates over tune IDs on TheSession.org in batches and saves results incrementally to `tunes.json`.

```bash
python session_tunes.py
```

Note: scraping ~22,000 tune pages takes significant time. The included `tunes.json` file can be used directly without re-running the scraper.

## Dependencies

```
numpy
pandas
matplotlib
scipy
statsmodels
requests
beautifulsoup4
```

## Acknowledgements

The `DiffMeansPermute` class used in the hypothesis testing section is adapted from Allen B. Downey's [ThinkStats2](https://github.com/AllenDowney/ThinkStats2) (MIT License).

This project began as a classroom assignment for DSC 530 (Data Exploration and Analysis) and was subsequently revised for public presentation.
