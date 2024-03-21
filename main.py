from contextlib import asynccontextmanager
from http.client import HTTPException 
from typing import Optional
from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Todoos(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    Desc: str = Field(index=True)
     
class TodooUpdate(Todoos, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TodoosCreate(Todoos):
    pass


class TodoosRead(Todoos):
    id: int
    

class TodoosUpdate(SQLModel):
    Desc: Optional[str] = None
       
        

 
sqlite_url = f""

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    create_db_and_tables()
    yield
    
     

app: FastAPI = FastAPI(lifespan=lifespan)
 


@app.post("/todoos/")
def create_todoos(todoos: Todoos):
    with Session(engine) as session:
        session.add(todoos)
        session.commit()
        session.refresh(todoos)
        return todoos


@app.get("/todoos/")
def read_todoos():
    with Session(engine) as session:
        todoos = session.exec(select(Todoos)).all()
        return todoos
    

@app.patch("/todoos/{todoos_id}", response_model=TodoosRead)
def update_todoos(todoos_id: int, todoos: TodoosUpdate):
    with Session(engine) as session:
        existing_todoos = session.get(Todoos, todoos_id)
        if not existing_todoos:
            raise HTTPException(status_code=404, detail="Todo item not found")
        
        # Update the attributes of the existing todo item
        for key, value in todoos.dict(exclude_unset=True).items():
            setattr(existing_todoos, key, value)
        
        session.add(existing_todoos)
        session.commit()
        session.refresh(existing_todoos)
        return existing_todoos
   
    
@app.delete("/todoos/{todoos_id}")
def delete_todoos(todoos_id: int):
    with Session(engine) as session:
        todoos = session.get(Todoos, todoos_id)
        if not todoos:
            raise HTTPException(status_code=404, detail="Todo item not found")
        session.delete(todoos)
        session.commit()
        return {"ok": True}
