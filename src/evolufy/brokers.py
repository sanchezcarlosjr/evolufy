from evolufy.information import AvailableInformation

class Broker:
    api_key: str
    def execute_income_policy_based_on(self, information: AvailableInformation):
        return information

class GBMPlus(Broker):
    pass

class EToro(Broker):
    pass