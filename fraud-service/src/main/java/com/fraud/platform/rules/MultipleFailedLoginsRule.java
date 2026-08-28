package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;

import java.util.Map;
import java.util.Optional;

public class MultipleFailedLoginsRule implements FraudRule {

    private final RulesProperties properties;

    public MultipleFailedLoginsRule(RulesProperties properties) {
        this.properties = properties;
    }

    @Override
    public Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context) {
        int failedCount = context.recentFailedLoginCount();
        if (failedCount < properties.failedLoginThreshold()) {
            return Optional.empty();
        }

        return Optional.of(new RuleEvaluation(
                RuleName.MULTIPLE_FAILED_LOGINS,
                properties.weights().multipleFailedLogins(),
                Map.of(
                        "failed_login_count", failedCount,
                        "window_minutes", properties.failedLoginWindowMinutes(),
                        "threshold", properties.failedLoginThreshold(),
                        "detail",
                        "%d failed logins within %d minutes (threshold %d)"
                                .formatted(
                                        failedCount,
                                        properties.failedLoginWindowMinutes(),
                                        properties.failedLoginThreshold()))));
    }
}
