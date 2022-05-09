from enum import Enum


class Action(Enum):
    Buy = 1
    Sell = 2
    NotBuy = 3
    NotSell = 4,
    NoAction = 5 # placeholder


class Reason(Enum):
    StopLoss = 1
    SafeExit = 2
    MainCriteriaMatch = 3
    MainCriteriaNotMatch = 4
    NoReason = 5
    AfterStopLoss = 6


class AlgoProcessingResult:

    def __init__(self, action=Action.NoAction, reason=Reason.NoReason):
        self.__action = action
        self.__reason = reason

    def __repr__(self):
        return f"Algo result: [{self.__action.name}], reason - {self.__reason.name}"

    def should_buy(self) -> bool:
        return self.__action == Action.Buy

    def should_sell(self) -> bool:
        return self.__action == Action.Sell

    def get_reason(self) -> str:
        return self.__reason.name


