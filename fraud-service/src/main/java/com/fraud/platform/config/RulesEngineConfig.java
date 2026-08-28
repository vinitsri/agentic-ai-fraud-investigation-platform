package com.fraud.platform.config;

import com.fraud.platform.rules.FraudRule;
import com.fraud.platform.rules.GeographicAnomalyRule;
import com.fraud.platform.rules.HighTransactionAmountRule;
import com.fraud.platform.rules.MultipleFailedLoginsRule;
import com.fraud.platform.rules.NewDeviceRule;
import com.fraud.platform.rules.NewLocationRule;
import com.fraud.platform.rules.TransactionVelocityRule;
import com.fraud.platform.rules.UnusualMerchantCategoryRule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class RulesEngineConfig {

    @Bean
    List<FraudRule> fraudRules(RulesProperties properties) {
        return List.of(
                new HighTransactionAmountRule(properties),
                new NewDeviceRule(properties),
                new NewLocationRule(properties),
                new TransactionVelocityRule(properties),
                new MultipleFailedLoginsRule(properties),
                new UnusualMerchantCategoryRule(properties),
                new GeographicAnomalyRule(properties));
    }
}
