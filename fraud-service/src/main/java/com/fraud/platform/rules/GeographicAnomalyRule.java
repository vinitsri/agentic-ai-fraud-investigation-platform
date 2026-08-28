package com.fraud.platform.rules;

import com.fraud.platform.config.RulesProperties;
import com.fraud.platform.domain.RuleEvaluation;
import com.fraud.platform.domain.RuleName;
import com.fraud.platform.domain.TransactionEvaluationContext;
import com.fraud.platform.domain.TransactionRecord;
import com.fraud.platform.util.GeoUtils;

import java.math.BigDecimal;
import java.time.Duration;
import java.util.Map;
import java.util.Optional;

public class GeographicAnomalyRule implements FraudRule {

    private final RulesProperties properties;

    public GeographicAnomalyRule(RulesProperties properties) {
        this.properties = properties;
    }

    @Override
    public Optional<RuleEvaluation> evaluate(TransactionEvaluationContext context) {
        TransactionRecord txn = context.transaction();
        if (txn.latitude() == null || txn.longitude() == null) {
            return Optional.empty();
        }

        double txnLat = txn.latitude().doubleValue();
        double txnLon = txn.longitude().doubleValue();

        BigDecimal homeLat = context.customer().homeLatitude();
        BigDecimal homeLon = context.customer().homeLongitude();
        if (homeLat != null && homeLon != null) {
            double distanceFromHome = GeoUtils.haversineKm(
                    homeLat.doubleValue(), homeLon.doubleValue(), txnLat, txnLon);
            if (distanceFromHome >= properties.geographicAnomalyKm()) {
                return Optional.of(new RuleEvaluation(
                        RuleName.GEOGRAPHIC_ANOMALY,
                        properties.weights().geographicAnomaly(),
                        Map.of(
                                "distance_km", distanceFromHome,
                                "home_city", context.customer().homeCity(),
                                "home_country", context.customer().homeCountry(),
                                "transaction_city", txn.city(),
                                "transaction_country", txn.country(),
                                "detail",
                                "Transaction %.0f km from customer home (threshold %.0f km)"
                                        .formatted(distanceFromHome, properties.geographicAnomalyKm()))));
            }
        }

        TransactionRecord lastTxn = context.lastTransaction();
        if (lastTxn != null
                && lastTxn.latitude() != null
                && lastTxn.longitude() != null
                && lastTxn.createdAt() != null) {
            double hoursBetween = Duration.between(lastTxn.createdAt(), txn.createdAt()).toMinutes() / 60.0;
            if (hoursBetween <= properties.impossibleTravelHours()) {
                double travelDistance = GeoUtils.haversineKm(
                        lastTxn.latitude().doubleValue(),
                        lastTxn.longitude().doubleValue(),
                        txnLat,
                        txnLon);
                if (travelDistance >= properties.impossibleTravelKm()) {
                    return Optional.of(new RuleEvaluation(
                            RuleName.GEOGRAPHIC_ANOMALY,
                            properties.weights().geographicAnomaly(),
                            Map.of(
                                    "distance_km", travelDistance,
                                    "hours_between_transactions", hoursBetween,
                                    "last_transaction_id", lastTxn.transactionId(),
                                    "detail",
                                    "Impossible travel: %.0f km in %.1f hours (threshold %.0f km in %.0f hours)"
                                            .formatted(
                                                    travelDistance,
                                                    hoursBetween,
                                                    properties.impossibleTravelKm(),
                                                    properties.impossibleTravelHours()))));
                }
            }
        }

        return Optional.empty();
    }
}
