from router.authentication import router
from router.project import router_project
from router.task import router_task
from fastapi import FastAPI

app = FastAPI()

app.include_router(router)
app.include_router(router_project, prefix="/project")
app.include_router(router_task, prefix="/task")



