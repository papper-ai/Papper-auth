from fastapi import FastAPI
from sqladmin import Admin

from auth.router import auth_router
from repositories.models import SecretsAdmin, UsersAdmin
from repositories.postgres_repository import engine

app = FastAPI()
app.include_router(auth_router)

admin = Admin(app, engine)
admin.add_view(SecretsAdmin)
admin.add_view(UsersAdmin)


@app.get("/")
async def root():
    return {"message": "Hello World"}


