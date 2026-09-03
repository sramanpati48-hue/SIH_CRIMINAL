"""Configuration settings and thresholds for graph analytics."""

import os
from pydantic_settings import BaseSettings


class AnalyticsConfig(BaseSettings):
    """Typed configuration for analytics pattern thresholds."""
    
    # Pattern Thresholds
    MIN_CASES_CROSS_CONNECTOR: int = 3
    MIN_SHARED_PHONE: int = 2
    MIN_SHARED_VEHICLE: int = 2
    
    MIN_REPEATED_LOCATION_EVENTS: int = 3
    REPEATED_LOCATION_WINDOW_HOURS: int = 72
    
    MIN_TRANSACTION_CHAIN_LENGTH: int = 3
    TRANSACTION_CHAIN_WINDOW_HOURS: int = 48
    
    MIN_BRIDGE_COMMUNITIES: int = 2
    HIGH_CONNECTIVITY_PERCENTILE: float = 0.90

    # Operational Limits (Synthetic Demo Defaults)
    ANALYTICS_MAX_NODES: int = 1000
    ANALYTICS_MAX_EDGES: int = 5000
    ANALYTICS_MAX_DEPTH: int = 3
    
    # Versioning
    ANALYTICS_RULE_VERSION: str = "v1.0.0"
    ANALYTICS_ALGORITHM_VERSION: str = "nx-1.0.0"

    # Development Identity
    DEV_REVIEWER_ID: str = os.getenv("DEV_REVIEWER_ID", "DEV-USER-001")

    class Config:
        env_prefix = ""


# Global singleton instance
analytics_settings = AnalyticsConfig()
