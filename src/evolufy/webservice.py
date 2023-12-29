import ray
import requests
from fastapi import FastAPI
from ray import serve
from evolufy import pipeline

app = FastAPI()


# https://docs.ray.io/en/latest/serve/http-guide.html
# https://github.com/aiortc/aiortc/blob/main/examples/server/server.py
@serve.deployment
@serve.ingress(app)
class WebService:
    def __init__(self):
        self.predict = pipeline()

    @app.get("/")
    def root(self):
        return f"{self.x}, world!"

    @app.post("/predict")
    def predict_with(self):
        return self.predict()