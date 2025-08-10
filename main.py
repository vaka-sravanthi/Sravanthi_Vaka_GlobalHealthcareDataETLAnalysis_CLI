import argparse
from mysql_handler import MySQLHandler
from api_client import APIClient
from data_transformer import transform_data, transform_vaccine_data
from tabulate import tabulate
from decimal import Decimal

def format_large_numbers(results):
    formatted = []
    for row in results:
        formatted_row = []
        for item in row:
            if isinstance(item, (float, int, Decimal)):
                formatted_row.append(f"{int(item):,}")
            else:
                formatted_row.append(item)
        formatted.append(formatted_row)
    return formatted

def fetch_data(args):
    client = APIClient()
    db = MySQLHandler()
    try:
        raw_data = client.fetch_data(args.country, args.start_date, args.end_date)
        transformed = transform_data(raw_data)
        db.insert_data("covid_stats", transformed)
        print(f" {len(transformed)} records inserted for {args.country}")
    finally:
        db.close()

def query_data(args):
    db = MySQLHandler()
    try:
        query_type = args.query_type
        country = args.country
        metric = args.metric
        n = args.n

        if query_type == "daily_trends":
            query = f"""
                SELECT date, {metric}
                FROM covid_stats
                WHERE country = %s
                ORDER BY date
            """
            results = db.query(query, (country,))
            print(tabulate(format_large_numbers(results), headers=["Date", metric.capitalize()], tablefmt="grid"))

        elif query_type == "total_cases":
            query = """
                SELECT country, SUM(cases) AS total_cases
                FROM covid_stats
                GROUP BY country
                ORDER BY total_cases DESC
            """
            results = db.query(query)
            print(tabulate(format_large_numbers(results), headers=["Country", "Total Cases"], tablefmt="grid"))

        elif query_type == "top_n_countries_by_metric":
            query = f"""
                SELECT country, SUM({metric}) AS total
                FROM covid_stats
                GROUP BY country
                ORDER BY total DESC
                LIMIT %s
            """
            results = db.query(query, (n,))
            print(tabulate(format_large_numbers(results), headers=["Country", f"Total {metric.capitalize()}"], tablefmt="grid"))

        else:
            print("Invalid COVID query type.")
    finally:
        db.close()

def fetch_vaccine_data(args):
    client = APIClient()
    db = MySQLHandler()
    try:
        raw_data = client.fetch_vaccine_data(args.country, args.start_date, args.end_date)
        transformed = transform_vaccine_data(raw_data)
        db.insert_data_vaccine("vaccination_data", transformed)
        print(f" {len(transformed)} vaccine records inserted for {args.country}")
    finally:
        db.close()

def query_data_vaccine(args):
    db = MySQLHandler()
    try:
        query_type = args.query_type
        country = args.country
        n = args.n

        if query_type == "daily_trends":
            query = """
                SELECT date, vaccinations
                FROM vaccination_data
                WHERE country = %s
                ORDER BY date
            """
            results = db.query(query, (country,))
            print(tabulate(format_large_numbers(results), headers=["Date", "Vaccinations"], tablefmt="grid"))

        elif query_type == "total_vaccinations":
            query = """
                SELECT country, SUM(vaccinations) AS total_vaccinations
                FROM vaccination_data
                GROUP BY country
                ORDER BY total_vaccinations DESC
            """
            results = db.query(query)
            print(tabulate(format_large_numbers(results), headers=["Country", "Total Vaccinations"], tablefmt="grid"))

        elif query_type == "top_n_countries_by_vaccines":
            query = """
                SELECT country, SUM(vaccinations) AS total_vaccinations
                FROM vaccination_data
                GROUP BY country
                ORDER BY total_vaccinations DESC
                LIMIT %s
            """
            results = db.query(query, (n,))
            print(tabulate(format_large_numbers(results), headers=["Country", "Total Vaccinations"], tablefmt="grid"))

        else:
            print("Invalid vaccine query type.")
    finally:
        db.close()

def list_tables(_):
    db = MySQLHandler()
    try:
        tables = db.list_tables()
        print(" Available Tables:")
        for (table,) in tables:
            print(f" - {table}")
    finally:
        db.close()

def drop_tables(_):
    db = MySQLHandler()
    try:
        tables = db.list_tables()
        for (table,) in tables:
            db.cursor.execute(f"DROP TABLE IF EXISTS {table}")
        db.conn.commit()
        print(" All tables dropped.")
    finally:
        db.close()

def drop_table(args):
    db = MySQLHandler()
    try:
        db.cursor.execute(f"DROP TABLE IF EXISTS {args.table}")
        db.conn.commit()
        print(f"Table '{args.table}' dropped successfully.")
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description=" Global Healthcare Data ETL & CLI Analysis Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch_data", help="Fetch and store COVID data for a country")
    fetch_parser.add_argument("country", help="Country name")
    fetch_parser.add_argument("start_date", help="Start date in YYYY-MM-DD")
    fetch_parser.add_argument("end_date", help="End date in YYYY-MM-DD")
    fetch_parser.set_defaults(func=fetch_data)

    query_parser = subparsers.add_parser("query_data", help="Query the COVID database")
    query_parser.add_argument("query_type", choices=[
        "total_cases", "daily_trends", "top_n_countries_by_metric"
    ])
    query_parser.add_argument("--country", help="Country name", default=None)
    query_parser.add_argument("--metric", help="Metric: cases, deaths, recovered", default="cases")
    query_parser.add_argument("--n", type=int, help="Number of top countries")
    query_parser.set_defaults(func=query_data)

    vaccine_fetch_parser = subparsers.add_parser("fetch_vaccine_data", help="Fetch and store vaccination data")
    vaccine_fetch_parser.add_argument("country", help="Country name")
    vaccine_fetch_parser.add_argument("start_date", help="Start date in YYYY-MM-DD")
    vaccine_fetch_parser.add_argument("end_date", help="End date in YYYY-MM-DD")
    vaccine_fetch_parser.set_defaults(func=fetch_vaccine_data)

    vaccine_query_parser = subparsers.add_parser("query_data_vaccine", help="Query the vaccination database")
    vaccine_query_parser.add_argument("query_type", choices=[
        "daily_trends", "total_vaccinations", "top_n_countries_by_vaccines"
    ])
    vaccine_query_parser.add_argument("--country", help="Country name", default=None)
    vaccine_query_parser.add_argument("--n", type=int, help="Number of top countries")
    vaccine_query_parser.set_defaults(func=query_data_vaccine)

    list_parser = subparsers.add_parser("list_tables", help="List all tables")
    list_parser.set_defaults(func=list_tables)

    drop_all_parser = subparsers.add_parser("drop_tables", help="Drop all tables")
    drop_all_parser.set_defaults(func=drop_tables)

    drop_one_parser = subparsers.add_parser("drop_table", help="Drop a specific table")
    drop_one_parser.add_argument("table", help="Table name")
    drop_one_parser.set_defaults(func=drop_table)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
