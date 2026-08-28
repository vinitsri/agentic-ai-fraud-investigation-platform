package com.fraud.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "fraud.rules")
public record RulesProperties(
        double alertThreshold,
        double highAmountMultiplier,
        double highAmountAbsolute,
        int velocityWindowMinutes,
        int velocityThreshold,
        int failedLoginWindowMinutes,
        int failedLoginThreshold,
        double geographicAnomalyKm,
        double impossibleTravelKm,
        double impossibleTravelHours,
        int newDeviceMaxAgeHours,
        double merchantRiskThreshold,
        WeightProperties weights,
        SeverityProperties severity
) {
    public record WeightProperties(
            double highTransactionAmount,
            double newDevice,
            double newLocation,
            double transactionVelocity,
            double multipleFailedLogins,
            double unusualMerchantCategory,
            double geographicAnomaly
    ) {}

    public record SeverityProperties(double critical, double high, double medium, double low) {}
}
