import copy

from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

import db.dbconfig as dbconfig

# link to your database
engine = create_engine(dbconfig.DB_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

session = None


def get_session():
    # global session
    # if session is None:
    #     session = Session()
    return Session()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    time = Column(String)
    is_buy = Column(Boolean)
    coin = Column(String)
    price = Column(Float)
    usdt_price = Column(Float)

    def by_or_sell(self):
        if self.is_buy:
            return "BUY"
        else:
            return "SELL"

    def __repr__(self):
        return f"{self.time} - {self.by_or_sell()}  [{self.coin}] Price: {self.price}, USDT: {self.usdt_price}"

    def copy(self):
        return copy.deepcopy(self)


class OrderDAO:

    def put_order(self, order: Order):
        session = get_session()
        session.add(order)
        session.commit()
        session.close()

    def get_orders(self) -> list:
        session = get_session()
        result = session.query(Order).all()
        session.close()
        return result

    def get_last_order(self, currency, is_buy) -> list:
        session = get_session()
        result = session.query(Order).filter_by(coin=currency, is_buy=is_buy).order_by(Order.id.desc()).first()
        session.close()
        return result

    def delete_all_orders(self):
        session = get_session()
        session.query(Order).delete()
        session.commit()
        session.close()


class Balance(Base):
    __tablename__ = "balances"

    currency = Column(String, primary_key=True)
    amount = Column(Float)

    def __repr__(self):
        return f"{self.currency}: {self.amount}"


class BalanceDAO:

    def get_balances(self):
        session = get_session()
        result = session.query(Balance).all()
        session.close()
        return result

    def get_balance(self, currency):
        session = get_session()
        balances = session.query(Balance).filter_by(currency=currency).all()
        if len(balances) == 0:
            self.set_balance(currency, 0)
        result = session.query(Balance).filter_by(currency=currency).first()
        session.close()
        return result

    def set_balance(self, currency, amount: float):
        session = get_session()
        session.merge(Balance(currency=currency, amount=amount))
        session.commit()
        session.close()

    def delete_all_balances(self):
        session = get_session()
        session.query(Balance).delete()
        session.commit()
        session.close()


Base.metadata.create_all(engine)
