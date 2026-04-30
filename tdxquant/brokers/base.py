from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import OrderRequest, Result


class BrokerAdapter(ABC):
    @abstractmethod
    def health_check(self) -> Result:
        raise NotImplementedError

    @abstractmethod
    def inspect(self) -> Result:
        raise NotImplementedError

    @abstractmethod
    def detect(self) -> Result:
        raise NotImplementedError

    @abstractmethod
    def buy(self, order: OrderRequest) -> Result:
        raise NotImplementedError
