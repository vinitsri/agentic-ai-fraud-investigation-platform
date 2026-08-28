INSERT INTO merchants (merchant_id, name, category_code, category_name, risk_score, country)
VALUES ('MER-TEST001', 'Risky Merchant', '7995', 'Gambling', 0.8500, 'US');

INSERT INTO customers (
    customer_id, first_name, last_name, email, date_of_birth, account_status,
    account_created_at, home_country, home_city, home_latitude, home_longitude,
    avg_transaction_amt
) VALUES (
    'CUST-TEST001', 'Jane', 'Doe', 'jane.doe@test.local', '1990-01-01', 'ACTIVE',
    NOW() - INTERVAL '365 days', 'US', 'New York', 40.712800, -74.006000, 100.00
);

INSERT INTO devices (
    device_id, device_type, os, browser, fingerprint_hash, first_seen_at, last_seen_at, is_trusted
) VALUES (
    'DEV-TRUSTED01', 'MOBILE', 'iOS', 'Safari', 'fp-trusted', NOW() - INTERVAL '180 days', NOW(), TRUE
);

INSERT INTO customer_devices (customer_id, device_id, first_associated_at, last_used_at, is_primary)
VALUES ('CUST-TEST001', 'DEV-TRUSTED01', NOW() - INTERVAL '180 days', NOW(), TRUE);

INSERT INTO transactions (
    transaction_id, customer_id, merchant_id, device_id, amount, currency, status,
    transaction_type, merchant_category, latitude, longitude, city, country, created_at
) VALUES (
    'TXN-HIST001', 'CUST-TEST001', 'MER-TEST001', 'DEV-TRUSTED01', 95.00, 'USD', 'COMPLETED',
    'PURCHASE', '5411', 40.712800, -74.006000, 'New York', 'US', NOW() - INTERVAL '2 hours'
);

INSERT INTO login_events (
    login_id, customer_id, device_id, ip_address, success, failure_reason, created_at
) VALUES
    ('LOGIN-F1', 'CUST-TEST001', NULL, '203.0.113.1', FALSE, 'INVALID_PASSWORD', NOW() - INTERVAL '20 minutes'),
    ('LOGIN-F2', 'CUST-TEST001', NULL, '203.0.113.2', FALSE, 'INVALID_PASSWORD', NOW() - INTERVAL '15 minutes'),
    ('LOGIN-F3', 'CUST-TEST001', NULL, '203.0.113.3', FALSE, 'INVALID_PASSWORD', NOW() - INTERVAL '10 minutes');

INSERT INTO devices (
    device_id, device_type, os, browser, fingerprint_hash, first_seen_at, last_seen_at, is_trusted
) VALUES (
    'DEV-ATTACK01', 'MOBILE', 'Android', 'Chrome Mobile', 'fp-attack', NOW() - INTERVAL '30 minutes', NOW(), FALSE
);

INSERT INTO transactions (
    transaction_id, customer_id, merchant_id, device_id, amount, currency, status,
    transaction_type, merchant_category, latitude, longitude, city, country, created_at
) VALUES (
    'TXN-SUSP001', 'CUST-TEST001', 'MER-TEST001', 'DEV-ATTACK01', 7500.00, 'USD', 'COMPLETED',
    'PURCHASE', '7995', 48.856600, 2.352200, 'Paris', 'FR', NOW()
);
