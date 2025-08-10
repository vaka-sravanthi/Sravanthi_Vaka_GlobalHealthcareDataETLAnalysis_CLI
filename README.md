# 🌍 Global Healthcare Data ETL & Analysis CLI  
### Developed by: Vaka Sravanthi

##  Project Overview
Global Healthcare Data ETL & Analysis CLI is a Python-based command-line application designed to automate the full ETL (Extract, Transform, Load) process for COVID-19 historical and vaccination data sourced from the disease.sh public API.

The system extracts real-time or historical data for a specified country and date range, cleans and structures it, and loads it into a MySQL database. Users can then perform a wide range of analytical queries such as tracking COVID-19 trends, viewing vaccination progress, identifying top affected countries, and generating global summaries directly from a user-friendly CLI interface.

This tool is especially valuable for data engineers and analysts looking to work with reliable, structured healthcare data in a real-world data pipeline environment.

## Problem Statement

Public APIs often return raw, unstructured, or inconsistent data. In the context of global healthcare monitoring, this leads to major challenges:  
- Missing values and inconsistent formats  
- Duplicate or redundant records  
- Difficulty in querying and visualizing data for analysis  
- Lack of integration between multiple healthcare datasets such as cases and vaccination coverage  

This project solves these issues by:  
- Automatically extracting COVID-19 historical and vaccination data via REST API  
- Cleaning and structuring the data using Python  
- Storing it in a MySQL database for reliable access  
- Providing a range of analytical CLI queries to generate insights on cases, deaths, recoveries, and vaccination progress  

## Skills and Technologies Used
### Programming Language
- **Python** – for scripting, data extraction, transformation, and CLI development


### Database
- **MySQL** – used for storing cleaned and structured data, and performing analytical queries

### API Source
- **[disease.sh](https://disease.sh)** – public API used to fetch historical COVID-19 data by country and date

### Python Libraries and Modules
- `requests` – for sending HTTP requests and handling API responses  
- `mysql-connector-python` – for connecting and interacting with the MySQL database  
- `argparse` – for handling command-line arguments and building the CLI  
- `tabulate` – for displaying query results in a well-formatted table in the terminal  
- `configparser` – for reading API and DB credentials from an external configuration file  
- `logging` – for tracking errors, operations, and debugging information


### Data Manipulation and Validation
- `datetime` – for working with and validating dates
- `data_transformer.py` – custom functions for cleaning and filtering API data

### Project Management
- `Git` – used for version control, collaborative development, and tracking code changes throughout the project lifecycle

# System Architecture
![Architecture Diagram](output_Images/ArchitectureDiagram.jpg)

# Global Healthcare Data ETL & Analysis CLI  Dashboard
![Dashboard](output_Images/Dashboard.mp4)




##  File & Module Structure
```bash
healthcare_etl_cli/
├── __pycache__/                 # Python bytecode cache folder
├── output_Images/               # Contains system architecture image and CLI output screenshots
│   ├── ArchitectureDiagram.jpg # System architecture image
│   ├── 1.jpg                   # CLI Output Screenshot 1
│   ├── 2.jpg                   # CLI Output Screenshot 2
│   ├── 3.jpg                   # CLI Output Screenshot 3
│   ├── 4.jpg                   # CLI Output Screenshot 4
│   ├── 5.jpg                   # CLI Output Screenshot 5
│   ├── 6.jpg                   # CLI Output Screenshot 6
│   ├── 7.jpg                   # CLI Output Screenshot 7
│   ├── 8.jpg                   # CLI Output Screenshot 8
│   ├── 9.jpg                   # CLI Output Screenshot 9
│   ├── 10.jpg                  # CLI Output Screenshot 10
│   ├── 11.jpg                  # CLI Output Screenshot 11
│   ├── 12.jpg                  # CLI Output Screenshot 12
│   ├── 13.jpg                  # CLI Output Screenshot 13
│   ├── 14.jpg                  # CLI Output Screenshot 14
│   ├── 15.jpg                  # CLI Output Screenshot 15
│   └── Dashboard.mp4           # CLI or dashboard demonstration video
├── sql/                        # SQL scripts folder
│   └── create_tables.sql       # SQL script to create required tables
├── api_client.py               # Handles data extraction from API or local JSON
├── config.ini                  # Stores API endpoints and DB credentials
├── countries.txt               # List of country names for data extraction
├── data_transformer.py         # Cleans and formats raw or JSON data
├── dashboard.py                # (Optional) Script for visual dashboard (if applicable)
├── main.py                     # CLI entry point and command handler
├── mysql_handler.py            # Connects to MySQL and performs CRUD operations
├── README.md                   # Complete project documentation and usage
├── requirements.txt            # Lists all required Python packages
```
##  Setup & Installation
 Follow the steps below to set up and run the project locally.
### Step 1. Clone the repository
Clone the project from GitHub using the following command:
```bash
git clone https://github.com/vaka-sravanthi/healthcare_etl_cli.git
cd healthcare_etl_cli
```
---
###  Step 2: Install Python Dependencies
Make sure Python 3.8 or higher is installed. Then install the required libraries:
```bash
pip install -r requirements.txt
```
---
###  Step 3: Configure the Project
Update the `config.ini` file with your MySQL and API settings:
```ini
[mysql]
host = localhost
user = root
password = your_password
database = healthcare_db

[api]
url = https://disease.sh/v3/covid-19/historical
vaccine_url = https://disease.sh/v3/covid-19/vaccine/coverage/countries
```
---
### Step 4: Set Up the MySQL Database

Ensure MySQL is running. Then execute the following to create the required table:

```bash
mysql -u root -p < sql/create_tables.sql
```

Or manually execute the SQL from `create_tables.sql` in your MySQL client.
Create table if not exists covid_stats (
    id int auto_increment primary key,
    country varchar(100) not null,
    date Date not null,
    cases int,
    deaths int,
    recovered int,
    last_updated timestamp default current_timestamp,
    unique (country, date)
);
Create table if not exsists vaccination_data (
    id int auto_increment primary key,
    country varchar(100) not null,
    date DATE not null,
    vaccinations bigint,
    last_updated timestamp default current_timestamp,
    unique(country, date)
);

---
---
###  Step 5: Run the Application
Now you're ready to use the CLI application.
#### Example1: Fetch Data
```bash
python main.py fetch_data <country> <start_date> <end_date>
```

```bash
python main.py fetch_data India 2023-01-01 2023-01-10
```

#### Example2: List Tables
```bash
python main.py list_tables
```

#### Example3: Run Query
## Data Query Commands

```bash
python main.py query_data <query_type> [--country <country>] [--metric <metric>] [--n <number>]
```

```bash
python main.py query_data top_n_countries_by_metric --metric deaths --n 5
```
### Example4: Drop specific table
```bash
python main.py drop_table covid_stats
```

---
### Example5: Drop all tables
```bash
python main.py drop_tables
```
### Example6: Total vaccinations by country
```bash
python main.py query_data_vaccine total_vaccinations
```
### Example7: Top N countries by total vaccinations
```bash
python main.py query_data_vaccine top_n_countries_by_vaccines --n 5
```
### Example8: Daily vaccination trends for a country
```bash
python main.py query_data_vaccine daily_trends --country USA
```

### Query Types:
- `total_cases`
- `daily_trends`
- `top_n_countries_by_metric`
- `global_summary`
- `countries_with_zero_deaths`
- `most_critical_cases`
- `recovered_rate_over_50`
- `show_all_for_country`
- `total_vaccinations`
- `daily_trends_vaccine`
- `top_n_countries_by_vaccines`
- `highest_single_day_vaccinations`
- `global_highest_single_day_vaccinations`
- `avg_daily_vaccinations`
- `countries_with_zero_vaccinations`
---

# Sample Output
## Output 1:HealthCare_cli_Intro
![healthcare_cli_intro](output_Images/1.jpg)
## Output 2:ETL Data Fetch Summary
![ETL Fetch Output](output_Images/2.jpg)
## Output 3: Database Tables Overview
![DatabaseOutputs](output_Images/3.jpg)
## Output 4:Total COVID-19 Cases by Country
![Total Cases Output](output_Images/5.jpg)
## Output 5:Top 5 Countries by Total COVID-19 Cases
![Top Cases Output](output_Images/6.jpg)
## Output 6:Global COVID-19 Summary
![Global Summary Output](output_Images/7.jpg)
## Output 7:Top 5 Countries by Total Deaths (Most Critical Cases)
![Most Critical Cases Output](output_Images/8.jpg)
## Output 8:Countries with Recovery Rate Over 50%
![Recovery Rate Over 50](output_Images/9.jpg)
## Output 9:COVID-19 Daily Statistics for India
![India Timeline](output_Images/10.jpg)
## Output 10:Drop Tables Output
![Drop Tables Output](output_Images/12.jpg)
## Output 11: Total Vaccinations by Country
![Total Vaccinations Output](output_Images/13.jpg)
## Output 12: Top 5 Countries by Total Vaccinations
![Top N Vaccinations Output](output_Images/14.jpg)
## Output 13: Daily Vaccination Trends for USA
![Daily Vaccination Trends Output](output_Images/15.jpg)

---
## Testing Checklist
- API fetch (COVID and vaccination data)
- Data cleaning and transformation
- Batch insert into MySQL
- CLI queries for COVID metrics
- CLI queries for vaccination metrics
- Argument validation for all commands
- Error logging and exception handling
- Output screenshot verification
- Database table creation and dropping
- Edge case handling (e.g., missing or zero data)
---

## References

- [disease.sh API - Historical COVID-19 Data](https://disease.sh/v3/covid-19/historical)
- [disease.sh API - Vaccination Data](https://disease.sh/v3/covid-19/vaccine/coverage)
- [MySQL Connector/Python Documentation](https://dev.mysql.com/doc/connector-python/en/)
- [Tabulate - Pretty Print Tables](https://pypi.org/project/tabulate/)
---

### Setup Complete
You are now ready to explore and analyze global healthcare data using the CLI!

## License
This project is for academic use only. All rights reserved © 2025 **Vaka Sravanthi**.








