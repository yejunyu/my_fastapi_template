from loguru import logger
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeWapPayModel import AlipayTradeWapPayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeWapPayRequest import AlipayTradeWapPayRequest
from app.core.config import settings
from app.models.interview import Order
from app.models.product import Product


class AlipayUtil:
    def __init__(
        self,
        app_id,
        app_private_key,
        alipay_public_key,
        notify_url,
        server_url="https://openapi.alipay.com/gateway.do",
    ):
        alipay_client_config = AlipayClientConfig()
        alipay_client_config.server_url = server_url
        alipay_client_config.app_id = app_id
        alipay_client_config.app_private_key = app_private_key
        alipay_client_config.alipay_public_key = alipay_public_key
        self.client = DefaultAlipayClient(
            alipay_client_config=alipay_client_config, logger=logger
        )
        self.notify_url = notify_url

    def create_payment(self, order: Order, product: Product, platform: str):
        """
        order: 订单对象，需有 order_no, amount
        product: 商品对象，需有 name, description
        platform: 'web' or 'app'
        """
        if platform == "web":
            model = AlipayTradePagePayModel()
            model.out_trade_no = order.order_no
            model.total_amount = str(order.amount / 100)  # 单位元
            model.subject = product.name
            model.body = product.description or product.name
            model.product_code = "FAST_INSTANT_TRADE_PAY"
            print(model.to_alipay_dict())
            request = AlipayTradePagePayRequest(biz_model=model)
            request.notify_url = self.notify_url
            # 返回支付链接（GET方式）
            pay_url = self.client.page_execute(request, http_method="GET")
            return {"url_str": pay_url}
        elif platform == "app":
            model = AlipayTradeWapPayModel()
            model.out_trade_no = order.order_no
            model.total_amount = str(order.amount / 100)
            model.subject = product.name
            model.body = product.description or product.name
            model.product_code = "QUICK_WAP_WAY"
            request = AlipayTradeWapPayRequest(biz_model=model)
            request.notify_url = self.notify_url
            # 返回app拉起支付串
            pay_str = self.client.page_execute(request, http_method="GET")
            return {"url_str": pay_str}
        else:
            raise ValueError(f"不支持的平台类型: {platform}")


alipay_pay_client = AlipayUtil(
    app_id=settings.ALIPAY_APP_ID,
    app_private_key=settings.ALIPAY_APP_PRIVATE_KEY,
    alipay_public_key=settings.ALIPAY_ALIPAY_PUBLIC_KEY,
    notify_url=settings.ALIPAY_NOTIFY_URL,
    server_url=settings.ALIPAY_SERVER_URL,
)
