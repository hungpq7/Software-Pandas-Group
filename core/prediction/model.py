class Model:
    def __init__(self, name):
        self.name = name
        self._load_model()

    def _load_model(self, path):
        self.model = None
    
    def predict(self, x, horizon=30):
        pass