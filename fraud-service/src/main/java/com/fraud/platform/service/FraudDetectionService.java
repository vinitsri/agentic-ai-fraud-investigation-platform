package com.fraud.platform.service;

import com.fraud.platform.domain.TransactionEvaluationContext;
import com.fraud.platform.engine.FraudRulesEngine;
import com.fraud.platform.engine.FraudRulesEngine.EngineResult;
import com.fraud.platform.repository.FraudDataRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class FraudDetectionService {

    private final FraudDataRepository repository;
    private final FraudRulesEngine rulesEngine;

    public FraudDetectionService(FraudDataRepository repository, FraudRulesEngine rulesEngine) {
        this.repository = repository;
        this.rulesEngine = rulesEngine;
    }

    public FraudAlertResult evaluateTransaction(String transactionId, boolean persist) {
        Optional<TransactionEvaluationContext> contextOpt = repository.buildEvaluationContext(transactionId);
        if (contextOpt.isEmpty()) {
            return null;
        }

        EngineResult engineResult = rulesEngine.evaluate(contextOpt.get());
        FraudAlertResult result = toAlertResult(contextOpt.get(), engineResult);

        if (persist && engineResult.alertWorthy()) {
            repository.saveAlert(result);
        }

        return result;
    }

    public FraudAlertResult getAlert(String alertId) {
        return repository.findAlertById(alertId).orElse(null);
    }

    FraudAlertResult evaluateContext(TransactionEvaluationContext context) {
        EngineResult engineResult = rulesEngine.evaluate(context);
        return toAlertResult(context, engineResult);
    }

    private FraudAlertResult toAlertResult(TransactionEvaluationContext context, EngineResult engineResult) {
        return new FraudAlertResult(
                FraudDataRepository.newAlertId(),
                context.transaction().transactionId(),
                context.transaction().customerId(),
                roundScore(engineResult.fraudScore()),
                engineResult.triggeredRules(),
                engineResult.severity().name(),
                engineResult.evidence(),
                engineResult.alertWorthy() ? "OPEN" : "NO_ALERT");
    }

    private double roundScore(double score) {
        return Math.round(score * 10000.0) / 10000.0;
    }

    public record FraudAlertResult(
            String alertId,
            String transactionId,
            String customerId,
            double fraudScore,
            List<String> triggeredRules,
            String severity,
            List<Map<String, Object>> evidence,
            String status
    ) {}
}
