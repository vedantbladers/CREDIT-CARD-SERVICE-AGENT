-- Initial schema for mock banking database
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    credit_limit NUMERIC(12, 2) NOT NULL DEFAULT 5000.00,
    fees_waived_this_quarter INT NOT NULL DEFAULT 0,
    tenure_months INT NOT NULL DEFAULT 12,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS card_replacements (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(32) NOT NULL REFERENCES accounts(account_number),
    reason VARCHAR(50) NOT NULL,
    delivery_type VARCHAR(50) NOT NULL DEFAULT 'standard',
    status VARCHAR(32) NOT NULL DEFAULT 'dispatched',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_transactions (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(32) NOT NULL REFERENCES accounts(account_number),
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) DEFAULT 0.00,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed accounts for testing
INSERT INTO accounts (account_number, name, balance, credit_limit, fees_waived_this_quarter, tenure_months, status) VALUES
('ACC-1001', 'Alice Johnson', 1450.50, 10000.00, 0, 18, 'active'),
('ACC-1002', 'Bob Smith', 320.00, 5000.00, 1, 3, 'active'),
('ACC-1003', 'Charlie Brown', 5820.75, 15000.00, 2, 24, 'suspended'),
('ACC-1004', 'Dana Scully', 890.00, 7500.00, 0, 14, 'fraud_alert')
ON CONFLICT (account_number) DO UPDATE SET
    credit_limit = EXCLUDED.credit_limit,
    tenure_months = EXCLUDED.tenure_months,
    status = EXCLUDED.status;
