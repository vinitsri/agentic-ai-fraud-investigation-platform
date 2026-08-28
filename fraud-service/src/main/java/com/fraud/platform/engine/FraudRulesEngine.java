package com.fraud.platform.engine;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.AlertSeverity;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;
import com.fraud.platform.rules.FraudRule;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Component
public class FraudRulesEngine {

    private final List<FraudRule> rules;
    private final RulesProperties properties;

    public FraudRulesEngine(List<FraudRule> rules, RulesProperties properties) {
        this.rules = rules;
        this.properties = properties;
    }

    public EngineResult evaluate(TransactionEvaluationContext context) {
        List<RuleEvaluation> triggered = new ArrayList<>();
        for (FraudRule rule : rules) {
            rule.evaluate(context).ifPresent(triggered::add);
        }

        double maxWeight = properties.weights().highTransactionAmount()
                + properties.weights().newDevice()
                + properties.weights().newLocation()
                + properties.weights().transactionVelocity()
                + properties.weights().multipleFailedLogins()
                + properties.weights().unusualMerchantCategory()
                + properties.weights().geographicAnomaly();

        double scoreWeight = triggered.stream().mapToDouble(RuleEvaluation::weight).sum();
        double fraudScore = maxWeight == 0 ? 0.0 : Math.min(1.0, scoreWeight / maxWeight);

        List<String> triggeredRuleNames = triggered.stream()
                .map(r -> r.rule().name())
                .toList();

        List<Map<String, Object>> evidence = triggered.stream()
                .map(this::toEvidenceEntry)
                .toList();

        AlertSeverity severity = determineSeverity(fraudScore);
        boolean alertWorthy = !triggered.isEmpty() && fraudScore >= properties.alertThreshold();

        return new EngineResult(fraudScore, triggeredRuleNames, severity, evidence, alertWorthy);
    }

    private Map<String, Object> toEvidenceEntry(RuleEvaluation evaluation) {
        Map<String, Object> entry = new LinkedHashMap<>();
        entry.put("rule", evaluation.rule().name());
        entry.put("weight", evaluation.weight());
        entry.putAll(evaluation.evidence());
        return entry;
    }

    private AlertSeverity determineSeverity(double fraudScore) {
        if (fraudScore >= properties.severity().critical()) {
            return AlertSeverity.CRITICAL;
        }
        if (fraudScore >= properties.severity().high()) {
            return AlertSeverity.HIGH;
        }
        if (fraudScore >= properties.severity().medium()) {
            return AlertSeverity.MEDIUM;
        }
        return AlertSeverity.LOW;
    }

    public record EngineResult(
            double fraudScore,
            List<String> triggeredRules,
            AlertSeverity severity,
            List<Map<String, Object>> evidence,
            boolean alertWorthy
    ) {}
}
