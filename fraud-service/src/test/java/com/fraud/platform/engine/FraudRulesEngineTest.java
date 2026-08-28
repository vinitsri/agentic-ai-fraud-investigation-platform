package com.fraud.platform.engine;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.AlertSeverity;
import com.fraud.platform.domain.CustomerDeviceRecord;
import com.fraud.platform.domain.CustomerRecord;
import com.fraud.platform.domain.MerchantRecord;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;
import com.fraud.platform.domain.TransactionRecord;
import com.fraud.platform.rules.FraudRule;
import com.fraud.platform.rules.GeographicAnomalyRule;
import com.fraud.platform.rules.HighTransactionAmountRule;
import com.fraud.platform.rules.MultipleFailedLoginsRule;
import com.fraud.platform.rules.NewDeviceRule;
import com.fraud.platform.rules.NewLocationRule;
import com.fraud.platform.rules.TransactionVelocityRule;
import com.fraud.platform.rules.UnusualMerchantCategoryRule;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.Set;

import static com.fraud.platform.rules.HighTransactionAmountRuleTest.testProperties;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class FraudRulesEngineTest {

    private FraudRulesEngine engine;

    @BeforeEach
    void setUp() {
        RulesProperties properties = testProperties();
        List<FraudRule> rules = List.of(
                new HighTransactionAmountRule(properties),
                new NewDeviceRule(properties),
                new NewLocationRule(properties),
                new TransactionVelocityRule(properties),
                new MultipleFailedLoginsRule(properties),
                new UnusualMerchantCategoryRule(properties),
                new GeographicAnomalyRule(properties));
        engine = new FraudRulesEngine(rules, properties);
    }

    @Test
    void evaluatesCleanTransactionWithNoRules() {
        Instant now = Instant.parse("2026-01-15T12:00:00Z");
        var context = new TransactionEvaluationContext(
                txn("TXN-1", "CUST-1", "DEV-1", new BigDecimal("50.00"), "US", "5411", now, 40.7, -74.0),
                customer("CUST-1", new BigDecimal("100.00"), 40.7, -74.0),
                merchant("MER-1", "5411", 0.1),
                List.of(new CustomerDeviceRecord("CUST-1", "DEV-1", now.minusSeconds(864000), true)),
                List.of(),
                List.of(txn("TXN-0", "CUST-1", "DEV-1", new BigDecimal("45.00"), "US", "5411", now.minusSeconds(3600), 40.7, -74.0)),
                null,
                0,
                Set.of("US"),
                Set.of("5411"));

        var result = engine.evaluate(context);
        assertTrue(result.triggeredRules().isEmpty());
        assertEquals(0.0, result.fraudScore());
        assertFalse(result.alertWorthy());
    }

    @Test
    void triggersMultipleRulesForSuspiciousTransaction() {
        Instant now = Instant.parse("2026-01-15T12:00:00Z");
        var context = new TransactionEvaluationContext(
                txn("TXN-2", "CUST-2", "DEV-NEW", new BigDecimal("8000.00"), "FR", "7995", now, 48.8566, 2.3522),
                customer("CUST-2", new BigDecimal("120.00"), 40.7128, -74.0060),
                merchant("MER-2", "7995", 0.85),
                List.of(),
                List.of(),
                List.of(txn("TXN-1", "CUST-2", "DEV-1", new BigDecimal("100.00"), "US", "5411", now.minusSeconds(300), 40.7128, -74.0060)),
                txn("TXN-1", "CUST-2", "DEV-1", new BigDecimal("100.00"), "US", "5411", now.minusSeconds(300), 40.7128, -74.0060),
                5,
                Set.of("US"),
                Set.of("5411"));

        var result = engine.evaluate(context);
        assertTrue(result.triggeredRules().contains(RuleName.HIGH_TRANSACTION_AMOUNT.name()));
        assertTrue(result.triggeredRules().contains(RuleName.NEW_DEVICE.name()));
        assertTrue(result.triggeredRules().contains(RuleName.NEW_LOCATION.name()));
        assertTrue(result.triggeredRules().contains(RuleName.MULTIPLE_FAILED_LOGINS.name()));
        assertTrue(result.triggeredRules().contains(RuleName.UNUSUAL_MERCHANT_CATEGORY.name()));
        assertTrue(result.triggeredRules().contains(RuleName.GEOGRAPHIC_ANOMALY.name()));
        assertTrue(result.fraudScore() >= 0.65);
        assertEquals(AlertSeverity.HIGH, result.severity());
        assertTrue(result.alertWorthy());
    }

    @Test
    void triggersVelocityRule() {
        Instant now = Instant.parse("2026-01-15T12:00:00Z");
        List<TransactionRecord> recent = List.of(
                txn("TXN-A", "CUST-3", "DEV-1", new BigDecimal("80"), "US", "5411", now.minusSeconds(60), 40.7, -74.0),
                txn("TXN-B", "CUST-3", "DEV-1", new BigDecimal("85"), "US", "5411", now.minusSeconds(120), 40.7, -74.0),
                txn("TXN-C", "CUST-3", "DEV-1", new BigDecimal("90"), "US", "5411", now.minusSeconds(180), 40.7, -74.0),
                txn("TXN-D", "CUST-3", "DEV-1", new BigDecimal("95"), "US", "5411", now.minusSeconds(240), 40.7, -74.0),
                txn("TXN-E", "CUST-3", "DEV-1", new BigDecimal("100"), "US", "5411", now.minusSeconds(300), 40.7, -74.0));

        var context = new TransactionEvaluationContext(
                txn("TXN-F", "CUST-3", "DEV-1", new BigDecimal("105"), "US", "5411", now, 40.7, -74.0),
                customer("CUST-3", new BigDecimal("100.00"), 40.7, -74.0),
                merchant("MER-1", "5411", 0.1),
                List.of(new CustomerDeviceRecord("CUST-3", "DEV-1", now.minusSeconds(864000), true)),
                recent,
                recent,
                recent.getLast(),
                0,
                Set.of("US"),
                Set.of("5411"));

        var result = engine.evaluate(context);
        assertTrue(result.triggeredRules().contains(RuleName.TRANSACTION_VELOCITY.name()));
    }

    private static TransactionRecord txn(
            String id,
            String customerId,
            String deviceId,
            BigDecimal amount,
            String country,
            String category,
            Instant createdAt,
            double lat,
            double lon) {
        return new TransactionRecord(
                id, customerId, "MER-1", deviceId, amount, "USD", category,
                BigDecimal.valueOf(lat), BigDecimal.valueOf(lon), "City", country, createdAt);
    }

    private static CustomerRecord customer(String id, BigDecimal avg, double lat, double lon) {
        return new CustomerRecord(id, avg, BigDecimal.valueOf(lat), BigDecimal.valueOf(lon), "HomeCity", "US");
    }

    private static MerchantRecord merchant(String id, String category, double risk) {
        return new MerchantRecord(id, category, "Category", BigDecimal.valueOf(risk));
    }
}
