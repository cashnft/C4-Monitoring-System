CREATE DATABASE monitoring_db;
\c monitoring_db

CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    service VARCHAR NOT NULL,
    metric_type VARCHAR NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    service VARCHAR NOT NULL,
    level VARCHAR NOT NULL,
    message VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS traces (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR NOT NULL,
    service VARCHAR NOT NULL,
    operation VARCHAR NOT NULL,
    duration FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);