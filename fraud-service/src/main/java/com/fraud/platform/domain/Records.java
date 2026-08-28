package com.fraud.platform.domain;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.Set;

public record TransactionRecord(
        String transactionId,
        String customerId,
        String merchantId,
        String deviceId,
        BigDecimal amount,
        String currency,
        String merchantCategory,
        BigDecimal latitude,
        BigDecimal longitude,
        String city,
        String country,
        Instant createdAt
) {}

public record CustomerRecord(
        String customerId,
        BigDecimal avgTransactionAmt,
        BigDecimal homeLatitude,
        BigDecimal homeLongitude,
        String homeCity,
        String homeCountry
) {}

public record MerchantRecord(
        String merchantId,
        String categoryCode,
        String categoryName,
        BigDecimal riskScore
) {}

public record CustomerDeviceRecord(
        String customerId,
        String deviceId,
        Instant firstAssociatedAt,
        boolean isPrimary
) {}

public record TransactionEvaluationContext(
        TransactionRecord transaction,
        CustomerRecord customer,
        MerchantRecord merchant,
        List<CustomerDeviceRecord> customerDevices,
        List<TransactionRecord> recentTransactions,
        List<TransactionRecord> historicalTransactions,
        TransactionRecord lastTransaction,
        int recentFailedLoginCount,
        Set<String> historicalCountries,
        Set<String> historicalMerchantCategories
) {}
