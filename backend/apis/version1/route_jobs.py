from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
# from db.models.jobs import Job
from db.models.users import User
from schemas.jobs import JobCreate, ShowJob
from db.repository.jobs import (create_new_job,
                                retrieve_job, list_jobs,
                                update_job_by_id,
                                delete_job_by_id)
from apis.version1.route_login import get_current_user_from_token
from typing import List

router = APIRouter()


@router.post("/create-job", response_model=ShowJob)
def create_job(job: JobCreate, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    owner_id = current_user.id
    job = create_new_job(job=job, db=db, owner_id=owner_id)
    return job


@router.get("/get/{job_id}", response_model=ShowJob)
def retrieve_job_by_id(job_id: int, db: Session = Depends(get_db)):
    job = retrieve_job(job_id=job_id, db=db)
    print(job)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Job with id {job_id} does not exist")
    return job


@router.get("/all", response_model=List[ShowJob])
def retrieve_all_jobs(db: Session = Depends(get_db)):
    jobs = list_jobs(db=db)
    return jobs


@router.put("/update/{job_id}")
def update_job(job_id: int, job: JobCreate, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user_from_token)):
    owner_id = current_user.id
    job_retrieved = retrieve_job(job_id=job_id, db=db)
    if not job_retrieved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Job with id {job_id} doe snot exist")
    if job_retrieved.owner_id == current_user.id or current_user.is_superuser:
        update_job_by_id(job_id=job_id, job=job, db=db, owner_id=owner_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to update")
    return {"detail": "Successfully updated data."}


@router.delete("/delete/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):

    job = retrieve_job(job_id=job_id, db=db)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Job with id {job_id} does not exist")
    if job.owner_id == current_user.id or current_user.is_superuser:
        delete_job_by_id(job_id=job_id, db=db, owner_id=current_user.id)
        return {"detail": "Job Successfully deleted"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You are not permitted")
