from scenarios.account_takeover import AccountTakeoverScenario
from scenarios.failed_login_attack import FailedLoginAttackScenario
from scenarios.fraud_ring import FraudRingScenario
from scenarios.geographic_anomaly import GeographicAnomalyScenario
from scenarios.high_value_fraud import HighValueFraudScenario
from scenarios.new_device_fraud import NewDeviceFraudScenario
from scenarios.normal import NormalScenario
from scenarios.velocity_attack import VelocityAttackScenario

SCENARIO_REGISTRY = {
    "normal": NormalScenario(),
    "high-value-fraud": HighValueFraudScenario(),
    "account-takeover": AccountTakeoverScenario(),
    "velocity-attack": VelocityAttackScenario(),
    "geographic-anomaly": GeographicAnomalyScenario(),
    "new-device-fraud": NewDeviceFraudScenario(),
    "failed-login-attack": FailedLoginAttackScenario(),
    "fraud-ring": FraudRingScenario(),
}

FRAUD_SCENARIOS = [name for name in SCENARIO_REGISTRY if name != "normal"]
