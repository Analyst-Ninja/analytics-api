from fastapi import APIRouter, Depends, HTTPException, Query
from api.db.session import get_session
from sqlmodel import Session, select, delete, func, case
from datetime import datetime, timedelta, timezone
from timescaledb.hyperfunctions import time_bucket
from typing import List

from .models import (
    EventModel, 
    EventListSchema,
    EventCreateSchema,
    # EventUpdateSchema,
    EventBucketSchema,
    get_utc_now
)


router = APIRouter()

# GET METHODS

DEFAULT_LOOKUP_PAGES=[
    "/","/about","/pricing","/contact",
    "/blog","/products","/login","/signup",
    "/dashboard","/settings"
]

@router.get("/", response_model=List[EventBucketSchema])
def read_events(
        duration: str = Query(default='1 day'),
        pages: List = Query(default=None),
        session: Session = Depends(get_session)
    ):
    # a bunch of rows
    # query = select(EventModel).order_by(EventModel.updated_at.desc()).limit(5) # Very rarely we use it from the api 
    lookup_pages = pages if isinstance(pages, list) and len(pages) > 0 else DEFAULT_LOOKUP_PAGES
    bucket=time_bucket(duration, EventModel.time)
    os_case=case(
        (EventModel.user_agent.ilike("%windows%"),"Windows"),
        (EventModel.user_agent.ilike("%macintosh%"),"MacOS"),
        (EventModel.user_agent.ilike("%iphone%"),"iOS"),
        (EventModel.user_agent.ilike("%android%"),"Android"),
        (EventModel.user_agent.ilike("%linux%"),"Linux"),
        else_="Other"
    ).label('operating_system')

    query=(
        select(
            bucket.label('bucket'), 
            os_case,
            EventModel.page.label('page'),
            func.count().label('count'),
            func.avg(EventModel.duration).label('average_duration')
        )
        .where(
            EventModel.page.in_(lookup_pages)
        )
        .group_by(
            bucket, 
            os_case,
            EventModel.page,
        )
        .order_by(
            bucket,
            EventModel.page
        )
    )
    result = session.exec(query).all()
    return result

@router.get("/{event_id}", response_model=EventModel)
def get_event(event_id: int, session: Session = Depends(get_session)):
    # a single rows
    query=select(EventModel).where(EventModel.id == event_id)
    result=session.exec(query).first()

    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return result

# POST METHOD
@router.post("/", response_model=EventModel)
def create_event(
    payload: EventCreateSchema,
    session: Session = Depends(get_session)
):
    data = payload.model_dump() # payload -> dict -> pydantic
    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj

# We are not allowing update here - hence commenting out
# PUT METHOD
# @router.put("/{event_id}", response_model=EventModel)
# def update_event(
#         event_id: int, 
#         payload: EventUpdateSchema,
#         session: Session = Depends(get_session)
#     ):

#     query=select(EventModel).where(EventModel.id == event_id)
#     obj=session.exec(query).first()

#     if not obj:
#         raise HTTPException(status_code=404, detail="Event not found")
    
#     data = payload.model_dump()

#     for k,v in data.items():
#         setattr(obj, k, v)
    
#     obj.updated_at=get_utc_now() 

#     session.add(obj)
#     session.commit()
#     session.refresh(obj)

#     return obj

# DELETE METHOD
@router.delete("/{event_id}", response_model=EventModel)
def delete_event(event_id: int, session: Session = Depends(get_session)):

    query=select(EventModel).where(EventModel.id == event_id)
    get_obj=session.exec(query).first()
    print(get_obj)

    if not get_obj:
        raise HTTPException(status_code=404, detail="Event not found")

    query=delete(EventModel).where(EventModel.id == event_id)
    obj=session.exec(query) 
    
    session.commit()

    return get_obj.id