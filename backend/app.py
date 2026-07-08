from Router.Auth import router
from fastapi import FastAPI, Depends, APIRouter,BackgroundTasks,Request

app = FastAPI()

app.include_router(router)



