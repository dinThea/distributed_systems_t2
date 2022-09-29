"""Defines the factory responses"""
from dataclasses import dataclass

from cadeia.domain.entities import Factory


@dataclass
class DebitFactoryResponse:
    """Response of an the factory debit use case
    """
    factory: Factory
