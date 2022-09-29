"""Defines the module use cases"""
from cadeia.app.store.requests import (
    DebitStoreRequest,
    CreditStoreRequest
)
from cadeia.app.store.responses import CreditStoreResponse, DebitStoreResponse
from cadeia.app.store.strategies import RequestCreditStrategy
from cadeia.domain.entities import (
    InventoryState,
    ProductClasses,
    sum_order_info_quantity,
    OrderInfo
)


class StoreReceiveCreditUseCase:
    """Use case to credit an store
    """

    def execute(self, request: CreditStoreRequest) -> CreditStoreResponse:
        """Executes the use case called when a store fullfills its credit request

        Args:
            request (CreditStoreRequest): Credit request response

        Returns:
            CreditStoreResponse: Response of creditting operation
        """

        to_exclude_idx = -1
        for idx, order in enumerate(request.store.pending_cd_orders[request.product_class]):
            if order.product_class == request.product_class and \
                    order.quantity == request.quantity_of_items:
                to_exclude_idx = idx

        if to_exclude_idx == -1:
            return CreditStoreResponse(
                store=request.store
            )

        request.store.warehouses[request.product_class].quantity_of_items += \
            request.quantity_of_items
        request.store.pending_cd_orders[request.product_class].pop(to_exclude_idx)

        request.store.warehouses[request.product_class].quantity_of_items = min(
            request.store.warehouses[request.product_class].quantity_of_items,
            request.product_class.value
        )
        request.store.warehouses[request.product_class].state = InventoryState.RED

        if request.store.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.GREEN.value:
            request.store.warehouses[request.product_class].state = InventoryState.GREEN
        elif request.store.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.YELLOW.value:
            request.store.warehouses[request.product_class].state = InventoryState.YELLOW

        return CreditStoreResponse(
            store=request.store
        )


class DebitStoreUseCase:
    """Use case of an purchase on a store
    """

    def __init__(
        self,
        request_credit_strategy: RequestCreditStrategy
    ):
        self._request_credit_strategy = request_credit_strategy

    def execute(self, request: DebitStoreRequest) -> DebitStoreResponse:
        """Executes the use case of buying on a store

        Args:
            request (DebitStoreRequest): Request info

        Returns:
            DebitStoreResponse: Response
        """
        success = True
        if request.store.warehouses[request.product_class].quantity_of_items > \
                request.quantity_of_items:
            request.store.warehouses[request.product_class].quantity_of_items -= \
                request.quantity_of_items
        else:
            success = False
        request.store.warehouses[request.product_class].state = InventoryState.RED

        if request.store.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.GREEN.value:
            request.store.warehouses[request.product_class].state = InventoryState.GREEN
        elif request.store.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.YELLOW.value:
            request.store.warehouses[request.product_class].state = InventoryState.YELLOW

        if request.store.warehouses[request.product_class].state == InventoryState.RED:
            expected_quantity_after_future_credit = sum(
                [request.store.warehouses[request.product_class].quantity_of_items,
                 sum_order_info_quantity(
                     request.store.pending_cd_orders[request.product_class])])

            if request.product_class.value > expected_quantity_after_future_credit:
                order = OrderInfo(
                    entity_id=request.store.store_id,
                    product_class=request.product_class,
                    quantity=request.product_class.value - expected_quantity_after_future_credit
                )
                self._request_credit_strategy.request_credit(
                    order_info=order
                )
                request.store.pending_cd_orders[request.product_class].append(order)
        return DebitStoreResponse(
            success=success,
            store=request.store
        )
