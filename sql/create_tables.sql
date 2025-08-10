CREATE TABLE IF NOT EXISTS covid_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    cases INT,
    deaths INT,
    recovered INT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (country, date)
);
CREATE TABLE IF NOT EXISTS vaccination_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    vaccinations BIGINT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (country, date)
);
