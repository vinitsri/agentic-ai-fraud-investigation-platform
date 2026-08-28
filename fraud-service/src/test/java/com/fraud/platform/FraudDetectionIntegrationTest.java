package com.fraud.platform;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.datasource.init.ScriptUtils;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class FraudDetectionIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("fraud_platform")
            .withUsername("fraud_user")
            .withPassword("test");

    @DynamicPropertySource
    static void registerDataSourceProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private DataSource dataSource;

    @Autowired
    private TestRestTemplate restTemplate;

    @LocalServerPort
    private int port;

    private static boolean schemaInitialized = false;

    @BeforeEach
    void setUpDatabase() throws Exception {
        if (!schemaInitialized) {
            try (Connection connection = dataSource.getConnection()) {
                ScriptUtils.executeSqlScript(connection, new ClassPathResource("schema.sql"));
            }
            schemaInitialized = true;
        }
        try (Connection connection = dataSource.getConnection()) {
            connection.createStatement().execute("TRUNCATE fraud_alerts, login_events, transactions, customer_devices, devices, customers, merchants CASCADE");
            ScriptUtils.executeSqlScript(connection, new ClassPathResource("test-data.sql"));
        }
    }

    @Test
    void evaluateSuspiciousTransactionReturnsStructuredAlert() {
        ResponseEntity<Map> response = restTemplate.postForEntity(
                "http://localhost:" + port + "/api/v1/fraud/evaluate/TXN-SUSP001?persist=true",
                null,
                Map.class);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        Map<String, Object> body = response.getBody();
        assertNotNull(body);
        assertEquals("TXN-SUSP001", body.get("transactionId"));
        assertNotNull(body.get("alertId"));
        assertNotNull(body.get("fraudScore"));
        assertTrue(((Number) body.get("fraudScore")).doubleValue() >= 0.65);
        assertEquals("OPEN", body.get("status"));

        @SuppressWarnings("unchecked")
        var triggeredRules = (java.util.List<String>) body.get("triggeredRules");
        assertTrue(triggeredRules.contains("HIGH_TRANSACTION_AMOUNT"));
        assertTrue(triggeredRules.contains("NEW_DEVICE"));
        assertTrue(triggeredRules.contains("NEW_LOCATION"));
        assertTrue(triggeredRules.contains("MULTIPLE_FAILED_LOGINS"));

        @SuppressWarnings("unchecked")
        var evidence = (java.util.List<Map<String, Object>>) body.get("evidence");
        assertNotNull(evidence);
        assertTrue(evidence.size() >= 4);
    }

    @Test
    void evaluateMissingTransactionReturnsNotFound() {
        ResponseEntity<Map> response = restTemplate.postForEntity(
                "http://localhost:" + port + "/api/v1/fraud/evaluate/TXN-MISSING?persist=false",
                null,
                Map.class);
        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
    }
}
