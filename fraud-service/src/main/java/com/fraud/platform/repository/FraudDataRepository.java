package com.fraud.platform.repository;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.CustomerDeviceRecord;
import com.fraud.platform.domain.CustomerRecord;
import com.fraud.platform.domain.MerchantRecord;
import com.fraud.platform.domain.TransactionEvaluationContext;
import com.fraud.platform.domain.TransactionRecord;
import com.fraud.platform.service.FraudDetectionService.FraudAlertResult;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

@Repository
public class FraudDataRepository {

    private final JdbcTemplate jdbcTemplate;
    private final RulesProperties rulesProperties;
    private final ObjectMapper objectMapper;

    public FraudDataRepository(
            JdbcTemplate jdbcTemplate, RulesProperties rulesProperties, ObjectMapper objectMapper) {
        this.jdbcTemplate = jdbcTemplate;
        this.rulesProperties = rulesProperties;
        this.objectMapper = objectMapper;
    }

    public Optional<TransactionRecord> findTransactionById(String transactionId) {
        List<TransactionRecord> rows = jdbcTemplate.query(
                """
                SELECT transaction_id, customer_id, merchant_id, device_id, amount, currency,
                       merchant_category, latitude, longitude, city, country, created_at
                FROM transactions WHERE transaction_id = ?
                """,
                transactionRowMapper(),
                transactionId);
        return rows.stream().findFirst();
    }

    public Optional<CustomerRecord> findCustomerById(String customerId) {
        List<CustomerRecord> rows = jdbcTemplate.query(
                """
                SELECT customer_id, avg_transaction_amt, home_latitude, home_longitude,
                       home_city, home_country
                FROM customers WHERE customer_id = ?
                """,
                (rs, rowNum) -> new CustomerRecord(
                        rs.getString("customer_id"),
                        rs.getBigDecimal("avg_transaction_amt"),
                        rs.getBigDecimal("home_latitude"),
                        rs.getBigDecimal("home_longitude"),
                        rs.getString("home_city"),
                        rs.getString("home_country")),
                customerId);
        return rows.stream().findFirst();
    }

    public Optional<MerchantRecord> findMerchantById(String merchantId) {
        List<MerchantRecord> rows = jdbcTemplate.query(
                """
                SELECT merchant_id, category_code, category_name, risk_score
                FROM merchants WHERE merchant_id = ?
                """,
                (rs, rowNum) -> new MerchantRecord(
                        rs.getString("merchant_id"),
                        rs.getString("category_code"),
                        rs.getString("category_name"),
                        rs.getBigDecimal("risk_score")),
                merchantId);
        return rows.stream().findFirst();
    }

    public List<CustomerDeviceRecord> findCustomerDevices(String customerId) {
        return jdbcTemplate.query(
                """
                SELECT customer_id, device_id, first_associated_at, is_primary
                FROM customer_devices WHERE customer_id = ?
                """,
                (rs, rowNum) -> new CustomerDeviceRecord(
                        rs.getString("customer_id"),
                        rs.getString("device_id"),
                        rs.getTimestamp("first_associated_at").toInstant(),
                        rs.getBoolean("is_primary")),
                customerId);
    }

    public List<TransactionRecord> findRecentTransactions(
            String customerId, Instant before, int windowMinutes, String excludeTransactionId) {
        return jdbcTemplate.query(
                """
                SELECT transaction_id, customer_id, merchant_id, device_id, amount, currency,
                       merchant_category, latitude, longitude, city, country, created_at
                FROM transactions
                WHERE customer_id = ?
                  AND created_at <= ?
                  AND created_at >= ? - make_interval(mins => ?)
                  AND transaction_id <> ?
                ORDER BY created_at DESC
                """,
                transactionRowMapper(),
                customerId,
                Timestamp.from(before),
                Timestamp.from(before),
                windowMinutes,
                excludeTransactionId);
    }

    public List<TransactionRecord> findHistoricalTransactions(
            String customerId, Instant before, String excludeTransactionId) {
        return jdbcTemplate.query(
                """
                SELECT transaction_id, customer_id, merchant_id, device_id, amount, currency,
                       merchant_category, latitude, longitude, city, country, created_at
                FROM transactions
                WHERE customer_id = ?
                  AND created_at < ?
                  AND transaction_id <> ?
                ORDER BY created_at DESC
                LIMIT 500
                """,
                transactionRowMapper(),
                customerId,
                Timestamp.from(before),
                excludeTransactionId);
    }

    public Optional<TransactionRecord> findLastTransactionBefore(
            String customerId, Instant before, String excludeTransactionId) {
        List<TransactionRecord> rows = jdbcTemplate.query(
                """
                SELECT transaction_id, customer_id, merchant_id, device_id, amount, currency,
                       merchant_category, latitude, longitude, city, country, created_at
                FROM transactions
                WHERE customer_id = ?
                  AND created_at < ?
                  AND transaction_id <> ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                transactionRowMapper(),
                customerId,
                Timestamp.from(before),
                excludeTransactionId);
        return rows.stream().findFirst();
    }

    public int countRecentFailedLogins(String customerId, Instant before, int windowMinutes) {
        Integer count = jdbcTemplate.queryForObject(
                """
                SELECT COUNT(*)
                FROM login_events
                WHERE customer_id = ?
                  AND success = FALSE
                  AND created_at <= ?
                  AND created_at >= ? - make_interval(mins => ?)
                """,
                Integer.class,
                customerId,
                Timestamp.from(before),
                Timestamp.from(before),
                windowMinutes);
        return count == null ? 0 : count;
    }

    public Optional<TransactionEvaluationContext> buildEvaluationContext(String transactionId) {
        Optional<TransactionRecord> transactionOpt = findTransactionById(transactionId);
        if (transactionOpt.isEmpty()) {
            return Optional.empty();
        }

        TransactionRecord transaction = transactionOpt.get();
        Optional<CustomerRecord> customerOpt = findCustomerById(transaction.customerId());
        Optional<MerchantRecord> merchantOpt = findMerchantById(transaction.merchantId());
        if (customerOpt.isEmpty() || merchantOpt.isEmpty()) {
            return Optional.empty();
        }

        Instant txnTime = transaction.createdAt();
        List<CustomerDeviceRecord> devices = findCustomerDevices(transaction.customerId());
        List<TransactionRecord> recentTransactions = findRecentTransactions(
                transaction.customerId(),
                txnTime,
                rulesProperties.velocityWindowMinutes(),
                transaction.transactionId());
        List<TransactionRecord> historicalTransactions = findHistoricalTransactions(
                transaction.customerId(), txnTime, transaction.transactionId());
        Optional<TransactionRecord> lastTransaction = findLastTransactionBefore(
                transaction.customerId(), txnTime, transaction.transactionId());
        int failedLogins = countRecentFailedLogins(
                transaction.customerId(), txnTime, rulesProperties.failedLoginWindowMinutes());

        Set<String> historicalCountries = new HashSet<>();
        Set<String> historicalCategories = new HashSet<>();
        for (TransactionRecord historical : historicalTransactions) {
            if (historical.country() != null && !historical.country().isBlank()) {
                historicalCountries.add(historical.country());
            }
            if (historical.merchantCategory() != null && !historical.merchantCategory().isBlank()) {
                historicalCategories.add(historical.merchantCategory());
            }
        }

        return Optional.of(new TransactionEvaluationContext(
                transaction,
                customerOpt.get(),
                merchantOpt.get(),
                devices,
                recentTransactions,
                historicalTransactions,
                lastTransaction.orElse(null),
                failedLogins,
                historicalCountries,
                historicalCategories));
    }

    public void saveAlert(FraudAlertResult alert) {
        jdbcTemplate.update(
                """
                INSERT INTO fraud_alerts (
                    alert_id, transaction_id, customer_id, status, severity,
                    rule_triggered, fraud_score, triggered_rules, evidence, triggered_at
                ) VALUES (?, ?, ?, ?, ?::alert_severity, ?, ?, ?::jsonb, ?::jsonb, NOW())
                ON CONFLICT (alert_id) DO NOTHING
                """,
                alert.alertId(),
                alert.transactionId(),
                alert.customerId(),
                alert.status(),
                alert.severity(),
                alert.triggeredRules().isEmpty() ? null : alert.triggeredRules().getFirst(),
                alert.fraudScore(),
                toJson(alert.triggeredRules()),
                toJson(alert.evidence()));
    }

    public Optional<FraudAlertResult> findAlertById(String alertId) {
        List<FraudAlertResult> rows = jdbcTemplate.query(
                """
                SELECT alert_id, transaction_id, customer_id, status, severity::text,
                       fraud_score, triggered_rules, evidence
                FROM fraud_alerts WHERE alert_id = ?
                """,
                this::mapAlert,
                alertId);
        return rows.stream().findFirst();
    }

    private FraudAlertResult mapAlert(ResultSet rs, int rowNum) throws SQLException {
        return new FraudAlertResult(
                rs.getString("alert_id"),
                rs.getString("transaction_id"),
                rs.getString("customer_id"),
                rs.getDouble("fraud_score"),
                readStringList(rs.getString("triggered_rules")),
                rs.getString("severity"),
                readEvidence(rs.getString("evidence")),
                rs.getString("status"));
    }

    private RowMapper<TransactionRecord> transactionRowMapper() {
        return (rs, rowNum) -> new TransactionRecord(
                rs.getString("transaction_id"),
                rs.getString("customer_id"),
                rs.getString("merchant_id"),
                rs.getString("device_id"),
                rs.getBigDecimal("amount"),
                rs.getString("currency"),
                rs.getString("merchant_category"),
                rs.getBigDecimal("latitude"),
                rs.getBigDecimal("longitude"),
                rs.getString("city"),
                rs.getString("country"),
                rs.getTimestamp("created_at").toInstant());
    }

    private String toJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to serialize JSON", ex);
        }
    }

    private List<String> readStringList(String json) {
        if (json == null || json.isBlank()) {
            return List.of();
        }
        try {
            return objectMapper.readValue(json, new TypeReference<>() {});
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to parse triggered_rules JSON", ex);
        }
    }

    private List<java.util.Map<String, Object>> readEvidence(String json) {
        if (json == null || json.isBlank()) {
            return List.of();
        }
        try {
            return objectMapper.readValue(json, new TypeReference<>() {});
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to parse evidence JSON", ex);
        }
    }

    public static String newAlertId() {
        return "ALERT-" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase();
    }
}
