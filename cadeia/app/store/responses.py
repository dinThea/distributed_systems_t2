
from dataclasses import dataclass

from cadeia.domain.entities import Store


@dataclass
class DebitStoreResponse:
    """Response of an the store debit use case
    """
    success: bool
    store: Store


@dataclass
class CreditStoreResponse:
    """Response of an store credit use case
    """
    store: Store
