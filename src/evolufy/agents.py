from evolufy.data_sources import *
from evolufy.information import *
from evolufy.brokers import *
from evolufy.investment_strategy import *
from injector import inject


@inject
@dataclass
class Agent:
    data_services: DataServices
    investment_strategy: InvestmentStrategy
    broker: Broker

    async def act(self):
        information = await self.data_services.request()
        self.investment_strategy.optimize(information)
        return self.broker.execute_income_policy_based_on(information)
