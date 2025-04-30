"""领域模型异常类"""

class DomainException(Exception):
    """领域异常基类"""
    pass

class OutfitItemLimitExceeded(DomainException):
    """穿搭衣物数量超出限制异常"""
    def __init__(self, message="穿搭衣物数量超出限制"):
        self.message = message
        super().__init__(self.message)

class InvalidOutfitConfiguration(DomainException):
    """无效的穿搭配置异常"""
    def __init__(self, message="无效的穿搭配置"):
        self.message = message
        super().__init__(self.message)

class DuplicateClothingItem(DomainException):
    """重复的衣物异常"""
    def __init__(self, message="衣物已存在"):
        self.message = message
        super().__init__(self.message) 