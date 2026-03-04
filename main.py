from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import models
from database import engine
from schema import schema

# Create the database tables
models.Base.metadata.create_all(bind=engine)

graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Parking Lot Management System")

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {"message": "Welcome to Parking Lot Management API. Go to /graphql for the GraphQL playground."}
