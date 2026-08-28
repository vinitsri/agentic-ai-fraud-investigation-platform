package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;

import java.util.Map;
import java.util.Optional;

public class NewLocationRule implements FraudRule {

    private final RulesProperties properties;

    public NewLocationRule(RulesProperties properties) {
        this.properties = properties;
    }

    @Override
    public Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context) {
        String country = context.transaction().country();
        if (country == null || country.isBlank()) {
            return Optional.empty();
        }

        if (context.historicalCountries().contains(country)) {
            return Optional.empty();
        }

        return Optional.of(new RuleEvaluation(
                RuleName.NEW_LOCATION,
                properties.weights().newLocation(),
                Map.of(
                        "transaction_country", country,
                        "transaction_city", context.transaction().city(),
                        "known_countries", context.historicalCountries(),
                        "detail",
                        "Transaction country %s not seen in customer history".formatted(country))));
    }
}
