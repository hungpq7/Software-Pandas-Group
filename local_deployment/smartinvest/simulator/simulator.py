import pandas as pd

class Simulator:
    def __init__(self, data, actor):
        """
        Simulate the stock market with a given actor and model
        Args:
            data: pd.DataFrame: data to simulate
            actor: Actor: actor which will update the portfolio
        """
        self.data = data
        self.actor = actor
    

    def simulate(self):
        """
        Simulate the stock market with a given actor and model
        """
        returns = []
        portfolio = []
        for i in range(len(self.data)):
            data = self.data.iloc[i]
            action = self.actor.get_action(data)
            self.actor.update_portfolio(action)

            returns.append( self.actor.get_current_returns() )
            portfolio.append( self.actor.get_current_portfolio() )

        return returns, portfolio

    def get_portfolio(self):
        """
        Get the portfolio of the actor
        """
        return self.actor.get_portfolio()
        
class Actor:
    def __init__(self, model, window_size=10):
        """
        Decision making and portfolio management
        Args:
            model: Model: model which will make investment decision
        """
        self.model = model
        self.historical_data = pd.DataFrame()

    def get_action(self, data=None):
        if data is not None:
            self.historical_data = pd.concat([self.historical_data, pd.DataFrame([data])])
        
        w
            
        return self.model.predict(self.historical_data)

    def get_current_returns(self):
        return self.model.get_current_returns()

    def get_current_portfolio(self):
        return self.model.get_current_portfolio()

