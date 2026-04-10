from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from db.database import engine, Base

import modules.user
import modules.project
import modules.task
import modules.subscription
import modules.plan
import modules.notification   # ✅ ADDED

from routes.user_routes import router as user_router
from routes.project_routes import router as project_router
from routes.task_routes import router as task_router
from routes.admin_routes import router as admin_router
from routes.subscription_routes import router as subscription_router
from routes.webhook_routes import router as webhook_router
from routes.notification_routes import router as notification_router   # ✅ ADDED


app = FastAPI()

app.include_router(user_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(admin_router)
app.include_router(subscription_router)
app.include_router(webhook_router)
app.include_router(notification_router)   # ✅ ADDED


Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"msg": "API Running"}