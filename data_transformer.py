def transform_data(data):
    transformed = []
    for record in data:
        country = record.get("country", "Unknown")
        date = record.get("date")
        try:
            cases = int(record.get("cases", 0))
        except (TypeError, ValueError):
            cases = 0

        try:
            deaths = int(record.get("deaths", 0))
        except (TypeError, ValueError):
            deaths = 0

        try:
            recovered = int(record.get("recovered", 0))
        except (TypeError, ValueError):
            recovered = 0

        transformed.append((country, date, cases, deaths, recovered))
    return transformed

def transform_vaccine_data(data):
    transformed = []
    for record in data:
        try:
            country = record[0] if isinstance(record, tuple) else record.get("country", "Unknown")
            date = record[1] if isinstance(record, tuple) else record.get("date")
            vaccinations = int(record[2] if isinstance(record, tuple) else record.get("vaccinations", 0))
        except (TypeError, ValueError):
            vaccinations = 0
        transformed.append((country, date, vaccinations))
    return transformed
