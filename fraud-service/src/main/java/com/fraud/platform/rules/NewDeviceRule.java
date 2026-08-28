package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.CustomerDeviceRecord;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;

import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;

public class NewDeviceRule implements FraudRule {

    private final RulesProperties properties;

    public NewDeviceRule(RulesProperties properties) {
        this.properties = properties;
    }

    @Override
    public Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context) {
        String deviceId = context.transaction().deviceId();
        if (deviceId == null || deviceId.isBlank()) {
            return Optional.of(new RuleEvaluation(
                    RuleName.NEW_DEVICE,
                    properties.weights().newDevice(),
                    Map.of(
                            "device_id", "unknown",
                            "detail", "Transaction has no associated device")));
        }

        Optional<CustomerDeviceRecord> association = context.customerDevices().stream()
                .filter(d -> deviceId.equals(d.deviceId()))
                .findFirst();

        if (association.isEmpty()) {
            return Optional.of(new RuleEvaluation(
                    RuleName.NEW_DEVICE,
                    properties.weights().newDevice(),
                    Map.of(
                            "device_id", deviceId,
                            "detail", "Device has never been associated with this customer")));
        }

        Instant txnTime = context.transaction().createdAt();
        Instant firstSeen = association.get().firstAssociatedAt();
        long hoursSinceAssociation = Duration.between(firstSeen, txnTime).toHours();

        if (hoursSinceAssociation <= properties.newDeviceMaxAgeHours()) {
            return Optional.of(new RuleEvaluation(
                    RuleName.NEW_DEVICE,
                    properties.weights().newDevice(),
                    Map.of(
                            "device_id", deviceId,
                            "first_associated_at", firstSeen.toString(),
                            "hours_since_association", hoursSinceAssociation,
                            "detail",
                            "Device first associated %.0f hours before transaction (threshold %d hours)"
                                    .formatted((double) hoursSinceAssociation, properties.newDeviceMaxAgeHours()))));
        }

        return Optional.empty();
    }
}
