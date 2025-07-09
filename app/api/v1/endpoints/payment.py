import json
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
    return {
        "order_no": order_no,
        "url_str": result.get("url_str"),
    }


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
async def payment_ali_notify(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    request: Request,
):
    """
    支付宝回调
    """
    # 获取POST的form数据
    form_data = await request.form()
    logger.info(f"Form data: {dict(form_data)}")
    form_data = dict(form_data)
    try:
        if form_data.get("trade_status") == "TRADE_SUCCESS":
            order = await db_session.execute(
                Select(models.Order).where(
                    models.Order.order_no == form_data.get("out_trade_no")
                )
            )
            order = order.scalar_one_or_none()
            if not order:
                logger.error(f"订单不存在: {form_data.get('out_trade_no')}")
                return {"code": 0, "msg": "success"}
            order.status = OrderStatus.PAID
            db_session.add(order)
            await db_session.commit()
            await db_session.refresh(order)
            # 根据订单查询商品信息和用户信息,然后增加用户积分
            product = await db_session.execute(
                Select(models.Product).where(models.Product.sku_id == order.product_id)
            )
            product = product.scalar_one_or_none()
            if not product:
                logger.error(f"商品不存在: {order.product_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在"
                )
            user = await db_session.execute(
                Select(models.User).where(models.User.id == order.user_id)
            )
            user = user.scalar_one_or_none()
            if not user:
                logger.error(f"用户不存在: {order.user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
                )
            user.points += product.duration_seconds
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            order.status = OrderStatus.COMPLETED
            db_session.add(order)
            await db_session.commit()
            await db_session.refresh(order)
    except Exception as e:
        logger.error(f"支付宝回调失败: {e}")
    return {"code": 0, "msg": "success"}
