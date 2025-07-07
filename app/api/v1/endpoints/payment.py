from typing import List, cast
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import Select
from app.core.response import UnifiedResponseRoute

from sqlalchemy.ext.asyncio import AsyncSession
from app import models
from app.api import deps
from app.models.interview import OrderStatus
from app.schemas.product import ProductPublic, PaymentInput
from app.schemas.order import OrderPublic
from loguru import logger

from fastuuid import uuid7
from app.utils import alipay_pay_client

router = APIRouter(
    prefix="/payment", tags=["支付相关"], route_class=UnifiedResponseRoute
)


@router.get("/list/props", response_model=List[ProductPublic])
async def list_props(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
):
    """
    获取商品的列表
    """
    result = await db_session.execute(
        Select(models.Product).where(models.Product.status == 1)
    )
    products = result.scalars().all()
    return [ProductPublic.model_validate(product) for product in products]


@router.post("/pay")
async def pay(
    *,
    request: PaymentInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    支付,暂时只支持支付宝
    """
    # 1. 查询商品信息
    product = await db_session.execute(
        Select(models.Product).where(models.Product.sku_id == request.prop_id)
    )
    product = product.scalar_one_or_none()
    if not product or product.status != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    # 2. 生成订单

    order_no = str(uuid7().hex)
    order = models.Order(
        order_no=order_no,
        user_id=current_user.id,
        product_id=product.sku_id,
        amount=product.price,
        status=OrderStatus.UNPAID,  # 假设0为待支付
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    # 3. 创建支付
    result = alipay_pay_client.create_payment(
        order=order,
        product=product,
        platform=request.platform.lower(),
    )
    return result


@router.post("/checkout/{order_no}", response_model=OrderPublic)
async def payment_checkout(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    order_no: str,
):
    """
    检查支付状态
    """
    result = await db_session.execute(
        Select(models.Order).where(models.Order.order_no == order_no)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return OrderPublic.model_validate(order)


@router.post("/ali/notify")
def payment_ali_notify(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    request: Request,
):
    """
    支付宝回调
    """
    logger.info(request.body)
    print(request.body)
    return {"code": 0, "msg": "success"}
