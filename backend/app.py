from router.authentication import router
from router.project import router_project
from router.task import router_task
from fastapi import FastAPI
from router.user_management import router_user_management
app = FastAPI()

#This will contain all the task and project functionality

app.include_router(router)
app.include_router(router_project, prefix="/project")
app.include_router(router_task, prefix="/task")
app.include_router(router_user_management)
