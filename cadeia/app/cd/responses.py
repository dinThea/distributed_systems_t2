"""Defines the distribution center responses"""
from dataclasses import dataclass

from cadeia.domain.entities import DistributionCenter


@dataclass
class DebitDistributionCenterResponse:
    """Response of an the distribution_center debit use case
    """
    distribution_center: DistributionCenter


@dataclass
class CreditDistributionCenterResponse:
    """Response of an distribution_center credit use case
    """
    distribution_center: DistributionCenter
