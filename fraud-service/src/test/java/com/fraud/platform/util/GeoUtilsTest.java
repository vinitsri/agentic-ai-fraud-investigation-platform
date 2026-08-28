package com.fraud.platform.util;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class GeoUtilsTest {

    @Test
    void calculatesDistanceBetweenKnownCities() {
        double nycToParis = GeoUtils.haversineKm(40.7128, -74.0060, 48.8566, 2.3522);
        assertTrue(nycToParis > 5800 && nycToParis < 5900);
    }
}
