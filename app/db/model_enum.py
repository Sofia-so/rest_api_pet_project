from enum import Enum


class ProductStatus(Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    ON_THE_WAY = "on_the_way"
