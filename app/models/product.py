from sqlalchemy import Column, Integer, String, Text
from .base import BaseModel


class Product(BaseModel):
    __tablename__ = "product"
    sku_id = Column(String(64), unique=True, nullable=False, comment="商品唯一标识")
    name = Column(String(255), nullable=False, comment="商品名称")
    price = Column(Integer, nullable=False, comment="价格，单位分")
    duration_seconds = Column(Integer, nullable=False, comment="服务时长，单位秒")
    description = Column(Text, default="", comment="商品描述")
    status = Column(Integer, default=1, comment="1=上架,0=下架")
