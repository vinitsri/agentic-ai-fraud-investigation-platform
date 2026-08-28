package com.fraud.platform.domain;

import java.util.Map;

public record RuleEvaluation(
        RuleName rule,
        double weight,
        Map<String, Object> evidence
) {}
