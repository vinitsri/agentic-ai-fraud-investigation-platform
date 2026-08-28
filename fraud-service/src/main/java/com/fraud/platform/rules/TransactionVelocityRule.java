package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;

import java.util.Map;
import java.util.Optional;

public class TransactionVelocityRule implements FraudRule {

    private final RulesProperties properties;

    public TransactionVelocityRule(RulesProperties properties) {
        this.properties = properties;
    }

    @Override
    public Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context) {
        int count = context.recentTransactions().size() + 1;
        if (count <= properties.velocityThreshold()) {
            return Optional.empty();
        }

        return Optional.of(new RuleEvaluation(
                RuleName.TRANSACTION_VELOCITY,
                properties.weights().transactionVelocity(),
                Map.of(
                        "transaction_count", count,
                        "window_minutes", properties.velocityWindowMinutes(),
                        "threshold", properties.velocityThreshold(),
                        "detail",
                        "%d transactions within %d minutes (threshold %d)"
                                .formatted(count, properties.velocityWindowMinutes(), properties.velocityThreshold()))));
    }
}
