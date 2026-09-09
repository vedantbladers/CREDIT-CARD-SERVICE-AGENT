-- Initial schema for mock banking database
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    fees_waived_this_quarter INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed accounts for testing
INSERT INTO accounts (account_number, name, balance, fees_waived_this_quarter) VALUES
('ACC-1001', 'Alice Johnson', 1450.50, 0),
('ACC-1002', 'Bob Smith', 320.00, 1),
('ACC-1003', 'Charlie Brown', 5820.75, 2)
ON CONFLICT (account_number) DO NOTHING;
