# Global-Household-Risk-Simulator

## Overview
The **Global Household Risk Simulator** is a Python-based Monte Carlo simulation that uses various parameters to model household financial stress for different countries. This project calculates tail risk metrics and stress probability in order to compare downside financial risk.

### View the full project and an explination of how it works here:
[Click Me](https://docs.google.com/document/d/1cNSnzjHtEkO-TqE0Io6NDIg7XZyJfu0q/edit?usp=sharing&ouid=105523170322060783243&rtpof=true&sd=true)

## Purpose
- Probability of a household to experience financial stress over a year
- Estimate how severe the worst-case outcomes are when stress occurs
- Represent inflation volatility, unemployment, and health cost exposure towards household risk
- Use Monte Carlo simulation and tail-risk metrics for worldwide comparison


## Data Sources
All data is sourced from **World Bank Open Data API**:
- Inflation (Consumer Price Index, annual %)
- Unemployment rate (% of labor force)
- Out-of-pocket health expenditure (% of total health spending)


## Project Structure
```text
src/
  ingest/        # Data ingestion (World Bank API)
  clean/         # Data cleaning and parameter estimation
  model/         # Monte Carlo simulation and risk metrics
  viz/           # Plot generation
data/
  raw/           # Cached raw datasets
  processed/     # Cleaned parameters and simulation outputs
  outputs/       # Generated plots
