from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from modules.project import Project
from schemas.project import ProjectCreate
from utils.security import get_current_user

# ✅ ADDED
from modules.subscription import Subscription

router = APIRouter()


@router.post("/projects")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    # ✅ Get subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).first()

    # ✅ Count projects
    project_count = db.query(Project).filter(
        Project.owner_id == user.id
    ).count()

    # 🔥 FINAL LOGIC
    if not subscription:
        # ❌ FREE → limit 3
        if project_count >= 3:
            raise HTTPException(
                status_code=403,
                detail="Free limit reached (3). Upgrade to Pro"
            )
    else:
        # ✅ PRO → unlimited
        pass

    # 🔹 ORIGINAL CODE
    new_project = Project(
        name=project.name,
        description=project.description,
        owner_id=user.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {"msg": "Project created"}


@router.get("/projects")
def get_projects(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    return projects


@router.get("/projects/{project_id}")
def get_single_project(
    project_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    updated_data: ProjectCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = updated_data.name
    project.description = updated_data.description

    db.commit()
    db.refresh(project)

    return {"msg": "Project updated"}


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"msg": "Project deleted"}