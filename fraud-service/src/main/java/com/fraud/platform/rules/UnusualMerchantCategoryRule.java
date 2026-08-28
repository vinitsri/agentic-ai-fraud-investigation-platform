package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;

import java.util.Map;
import java.util.Optional;

public class UnusualMerchantCategoryRule implements FraudRule {

    private final RulesProperties properties;

    public UnusualMerchantCategoryRule(RulesProperties properties) {
        this.properties = properties;
    }

    @Override
    public Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context) {
        String category = context.transaction().merchantCategory();
        double merchantRisk = context.merchant().riskScore().doubleValue();
        boolean unusualCategory = !context.historicalMerchantCategories().contains(category);
        boolean highRiskMerchant = merchantRisk >= properties.merchantRiskThreshold();

        if (!unusualCategory && !highRiskMerchant) {
            return Optional.empty();
        }

        return Optional.of(new RuleEvaluation(
                RuleName.UNUSUAL_MERCHANT_CATEGORY,
                properties.weights().unusualMerchantCategory(),
                Map.of(
                        "merchant_category", category,
                        "merchant_risk_score", merchantRisk,
                        "known_categories", context.historicalMerchantCategories(),
                        "unusual_category", unusualCategory,
                        "high_risk_merchant", highRiskMerchant,
                        "detail",
                        unusualCategory
                                ? "Merchant category %s not seen in customer history".formatted(category)
                                : "High-risk merchant category (risk score %.2f)".formatted(merchantRisk))));
    }
}
