package com.fraud.platform.rules;

import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.TransactionEvaluationContext;

import java.util.Optional;

public interface FraudRule {
    Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context);
}
