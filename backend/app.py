from router.authentication import router
from fastapi import FastAPI
from router.user_management import router_user_management
app = FastAPI()

app.include_router(router)
app.include_router(router_user_management)



