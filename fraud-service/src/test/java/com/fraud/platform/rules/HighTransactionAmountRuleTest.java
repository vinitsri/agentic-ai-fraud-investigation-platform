package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.CustomerDeviceRecord;
import com.fraud.platform.domain.CustomerRecord;
import com.fraud.platform.domain.MerchantRecord;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;
import com.fraud.platform.domain.TransactionRecord;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class HighTransactionAmountRuleTest {

    private HighTransactionAmountRule rule;

    @BeforeEach
    void setUp() {
        rule = new HighTransactionAmountRule(testProperties());
    }

    @Test
    void triggersWhenAmountExceedsThreshold() {
        var context = contextWithAmount(new BigDecimal("6000.00"), new BigDecimal("100.00"));
        var evaluation = rule.evaluate(context).orElseThrow();
        assertEquals(RuleName.HIGH_TRANSACTION_AMOUNT, evaluation.rule());
        assertTrue(evaluation.evidence().containsKey("detail"));
    }

    @Test
    void doesNotTriggerForNormalAmount() {
        var context = contextWithAmount(new BigDecimal("120.00"), new BigDecimal("100.00"));
        assertTrue(rule.evaluate(context).isEmpty());
    }

    private TransactionEvaluationContext contextWithAmount(BigDecimal amount, BigDecimal avg) {
        Instant now = Instant.parse("2026-01-15T12:00:00Z");
        return new TransactionEvaluationContext(
                new TransactionRecord(
                        "TXN-1", "CUST-1", "MER-1", "DEV-1", amount, "USD", "5411",
                        BigDecimal.valueOf(40.7), BigDecimal.valueOf(-74.0), "NYC", "US", now),
                new CustomerRecord("CUST-1", avg, BigDecimal.valueOf(40.7), BigDecimal.valueOf(-74.0), "NYC", "US"),
                new MerchantRecord("MER-1", "5411", "Grocery", BigDecimal.valueOf(0.1)),
                List.of(new CustomerDeviceRecord("CUST-1", "DEV-1", now.minusSeconds(86400), true)),
                List.of(),
                List.of(),
                null,
                0,
                Set.of("US"),
                Set.of("5411"));
    }

    static RulesProperties testProperties() {
        return new RulesProperties(
                0.25,
                5.0,
                3000.0,
                5,
                5,
                30,
                3,
                500.0,
                800.0,
                2.0,
                48,
                0.6,
                new RulesProperties.WeightProperties(0.25, 0.15, 0.15, 0.20, 0.20, 0.10, 0.25),
                new RulesProperties.SeverityProperties(0.85, 0.65, 0.45, 0.25));
    }
}
