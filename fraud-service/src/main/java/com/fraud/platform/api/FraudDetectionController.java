package com.fraud.platform.api;

import com.fraud.platform.service.FraudDetectionService;
import com.fraud.platform.service.FraudDetectionService.FraudAlertResult;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class FraudDetectionController {

    private final FraudDetectionService fraudDetectionService;

    public FraudDetectionController(FraudDetectionService fraudDetectionService) {
        this.fraudDetectionService = fraudDetectionService;
    }

    @GetMapping("/health")
    Map<String, String> health() {
        return Map.of("status", "ok", "service", "fraud-service");
    }

    @PostMapping("/fraud/evaluate/{transactionId}")
    ResponseEntity<FraudAlertResult> evaluate(
            @PathVariable String transactionId,
            @RequestParam(defaultValue = "true") boolean persist) {
        FraudAlertResult result = fraudDetectionService.evaluateTransaction(transactionId, persist);
        if (result == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(result);
    }

    @GetMapping("/fraud/alerts/{alertId}")
    ResponseEntity<FraudAlertResult> getAlert(@PathVariable String alertId) {
        FraudAlertResult result = fraudDetectionService.getAlert(alertId);
        if (result == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(result);
    }
}
