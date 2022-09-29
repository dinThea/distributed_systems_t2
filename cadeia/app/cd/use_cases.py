"""Defines the distribution center use cases"""
from cadeia.app.cd.requests import (
    DebitDistributionCenterRequest,
    CreditDistributionCenterRequest
)
from cadeia.app.cd.responses import (
    CreditDistributionCenterResponse,
    DebitDistributionCenterResponse
)
from cadeia.app.cd.strategies import CDRequestCreditStrategy, CDSendCreditStrategy
from cadeia.domain.entities import (
    InventoryState,
    ProductClasses,
    sum_order_info_quantity,
    OrderInfo
)


class DistributionCenterReceiveCreditUseCase:
    """Use case to credit an distributionCenter
    """

    def __init__(
        self,
        send_credit_strategy: CDSendCreditStrategy
    ):
        self._send_credit_strategy = send_credit_strategy

    def execute(self, request: CreditDistributionCenterRequest) -> CreditDistributionCenterResponse:
        """Executes the use case called when a distributionCenter fullfills its credit request

        Args:
            request (CreditDistributionCenterRequest): Credit request response

        Returns:
            CreditDistributionCenterResponse: Response of creditting operation
        """

        to_exclude_idx = -1
        for idx, order in enumerate(
            request.distribution_center.pending_factory_orders[request.product_class]
        ):
            if order.product_class == request.product_class and \
                    order.quantity == request.quantity_of_items:
                to_exclude_idx = idx

        if to_exclude_idx == -1:
            return CreditDistributionCenterResponse(
                distribution_center=request.distribution_center
            )
        request.distribution_center.warehouses[request.product_class].quantity_of_items += \
            request.quantity_of_items
        request.distribution_center.pending_factory_orders[request.product_class].pop(
            to_exclude_idx
        )

        request.distribution_center.warehouses[request.product_class].quantity_of_items = min(
            request.distribution_center.warehouses[request.product_class].quantity_of_items,
            request.product_class.value * request.distribution_center.warehouse_multiplier
        )

        if len(request.distribution_center.pending_store_orders[request.product_class]) > 0:
            if request.distribution_center.warehouses[request.product_class].quantity_of_items >= \
                    request.distribution_center.pending_store_orders[request.product_class][0].quantity:
                self._send_credit_strategy.send_credit(
                    request.distribution_center.pending_store_orders[request.product_class][0]
                )
                request.distribution_center.warehouses[request.product_class].quantity_of_items -= \
                    request.distribution_center.pending_store_orders[request.product_class][0].quantity
                request.distribution_center.pending_store_orders[request.product_class].pop(0)

        request.distribution_center.warehouses[request.product_class].state = InventoryState.RED

        if request.distribution_center.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.GREEN.value * request.distribution_center.warehouse_multiplier:
            request.distribution_center.warehouses[
                request.product_class
            ].state = InventoryState.GREEN
        elif request.distribution_center.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.YELLOW.value * request.distribution_center.warehouse_multiplier:
            request.distribution_center.warehouses[
                request.product_class
            ].state = InventoryState.YELLOW

        return CreditDistributionCenterResponse(
            distribution_center=request.distribution_center
        )


class DebitDistributionCenterUseCase:
    """Use case of an purchase on a distributionCenter
    """

    def __init__(
        self,
        request_credit_strategy: CDRequestCreditStrategy,
        send_credit_strategy: CDSendCreditStrategy
    ):
        self._request_credit_strategy = request_credit_strategy
        self._send_credit_strategy = send_credit_strategy

    def execute(self, request: DebitDistributionCenterRequest) -> DebitDistributionCenterResponse:
        """Executes the use case of buying on a distributionCenter

        Args:
            request (DebitDistributionCenterRequest): Request info

        Returns:
            DebitDistributionCenterResponse: Response
        """
        if request.distribution_center.warehouses[request.product_class].quantity_of_items > \
                request.quantity_of_items:
            request.distribution_center.warehouses[request.product_class].quantity_of_items -= \
                request.quantity_of_items
            self._send_credit_strategy.send_credit(OrderInfo(
                entity_id=request.store_id,
                product_class=request.product_class,
                quantity=request.quantity_of_items
            ))
        elif request.distribution_center.warehouses[request.product_class].quantity_of_items < \
                request.product_class.value * request.distribution_center.warehouse_multiplier:
            expected_quantity_after_future_credit = sum(
                [request.distribution_center.warehouses[request.product_class].quantity_of_items,
                    sum_order_info_quantity(
                        request.distribution_center.pending_factory_orders[request.product_class]
                ),
                    -sum_order_info_quantity(
                        request.distribution_center.pending_store_orders[request.product_class]
                )
                ])

            order = OrderInfo(
                entity_id=request.distribution_center.distribution_center_id, product_class=request.product_class,
                quantity=request.product_class.value * request.distribution_center.warehouse_multiplier -
                expected_quantity_after_future_credit)
            self._request_credit_strategy.request_credit(
                order_info=order
            )
            request.distribution_center.pending_factory_orders[request.product_class].append(order)
            request.distribution_center.pending_store_orders[request.product_class].append(OrderInfo(
                entity_id=request.store_id,
                product_class=request.product_class,
                quantity=request.quantity_of_items
            ))
            return DebitDistributionCenterResponse(request.distribution_center)

        request.distribution_center.warehouses[request.product_class].state = InventoryState.RED

        if request.distribution_center.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.GREEN.value * request.distribution_center.warehouse_multiplier:
            request.distribution_center.warehouses[
                request.product_class
            ].state = InventoryState.GREEN
        elif request.distribution_center.warehouses[request.product_class].quantity_of_items > \
                request.product_class.value * InventoryState.YELLOW.value * request.distribution_center.warehouse_multiplier:
            request.distribution_center.warehouses[
                request.product_class
            ].state = InventoryState.YELLOW

        if request.distribution_center.warehouses[
            request.product_class
        ].state == InventoryState.RED:
            expected_quantity_after_future_credit = sum(
                [request.distribution_center.warehouses[request.product_class].quantity_of_items,
                    sum_order_info_quantity(
                        request.distribution_center.pending_factory_orders[request.product_class]
                ),
                    -sum_order_info_quantity(
                        request.distribution_center.pending_store_orders[request.product_class]
                )
                ])

            order = OrderInfo(
                entity_id=request.distribution_center.distribution_center_id, product_class=request.product_class,
                quantity=request.product_class.value * request.distribution_center.warehouse_multiplier -
                expected_quantity_after_future_credit)
            self._request_credit_strategy.request_credit(
                order_info=order
            )
            request.distribution_center.pending_factory_orders[ProductClasses.A].append(order)
        return DebitDistributionCenterResponse(
            distribution_center=request.distribution_center
        )
