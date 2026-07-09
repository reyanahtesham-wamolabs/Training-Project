from Router.Authentication import router
from fastapi import FastAPI

app = FastAPI()

app.include_router(router)



