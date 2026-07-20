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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
