package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;
import com.fraud.platform.domain.TransactionRecord;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Optional;

public class HighTransactionAmountRule implements FraudRule {

    private final RulesProperties properties;

    public HighTransactionAmountRule(RulesProperties properties) {
        this.properties = properties;
    }

    @Override
    public Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context) {
        TransactionRecord txn = context.transaction();
        BigDecimal amount = txn.amount();
        BigDecimal avg = context.customer().avgTransactionAmt();
        double threshold = Math.max(
                properties.highAmountAbsolute(),
                avg.doubleValue() * properties.highAmountMultiplier());

        if (amount.doubleValue() <= threshold) {
            return Optional.empty();
        }

        return Optional.of(new RuleEvaluation(
                RuleName.HIGH_TRANSACTION_AMOUNT,
                properties.weights().highTransactionAmount(),
                Map.of(
                        "transaction_amount", amount,
                        "customer_avg_amount", avg,
                        "threshold", threshold,
                        "detail",
                        "Transaction amount %.2f exceeds threshold %.2f (avg %.2f x multiplier %.1f)"
                                .formatted(amount, threshold, avg, properties.highAmountMultiplier()))));
    }
}
