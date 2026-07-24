from router.authentication import router
from router.project import router_project
from router.task import router_task
from router.team import router_team
from router.notification import router_notification
from router.comment import router_comment
from router.activity import router_activity
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.user_management import router_user_management
from contextlib import asynccontextmanager
from fastapi import FastAPI
from scheduler.scheduler import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Includes all routers
app.include_router(router, prefix="/Auth", tags=["Authentication"])
app.include_router(router_project, prefix="/project", tags=["Project"])
app.include_router(router_task, prefix="/task", tags=["Task"])
app.include_router(router_user_management, prefix="/User", tags=["User"])
app.include_router(router_team, prefix="/Team", tags=["Team"])
app.include_router(router_notification, prefix="/Notification", tags=["Notification"])
app.include_router(router_comment, prefix="/comment", tags=["Comment"])
app.include_router(router_activity, prefix="/activity", tags=["Activity"])
