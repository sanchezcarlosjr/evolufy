from fastapi import FastAPI

app = FastAPI()


# https://docs.ray.io/en/latest/serve/http-guide.html
# https://github.com/aiortc/aiortc/blob/main/examples/server/server.py

class WebService:

    @app.get("/")
    def root(self):
        return f"Hello, world!"

    @app.post("/predict")
    def predict_with(self):
        return 0
