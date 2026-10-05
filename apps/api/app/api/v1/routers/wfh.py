from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user, get_employee_or_404, require_manager
from app.db.session import get_db
from app.models.wfh_request import WfhRequest
from app.schemas.wfh import WfhCreate, WfhOut, WfhReview
from app.services import wfh_service

router = APIRouter(prefix="/wfh", tags=["wfh"])


@router.post("", response_model=WfhOut, status_code=201)
def apply_wfh(
    payload: WfhCreate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.date_to < payload.date_from:
        raise HTTPException(status_code=400, detail="date_to must not precede date_from")

    employee = get_employee_or_404(db, user.employee_id)
    wfh_service.assert_approval_allowed(
        db,
        employee.id,
        payload.date_from,
        payload.date_to,
        employee.wfh_limit,
        WfhRequest,
    )

    req = WfhRequest(
        employee_id=employee.id,
        date_from=payload.date_from,
        date_to=payload.date_to,
        reason=payload.reason,
        status="pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/me", response_model=list[WfhOut])
def my_wfh(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(WfhRequest)
        .filter(WfhRequest.employee_id == user.employee_id)
        .order_by(WfhRequest.created_at.desc())
        .all()
    )


@router.get("/pending", response_model=list[WfhOut])
def pending_wfh(_: CurrentUser = Depends(require_manager), db: Session = Depends(get_db)):
    return (
        db.query(WfhRequest)
        .filter(WfhRequest.status == "pending")
        .order_by(WfhRequest.created_at.asc())
        .all()
    )


@router.post("/{wfh_id}/review", response_model=WfhOut)
def review_wfh(
    wfh_id: int,
    payload: WfhReview,
    user: CurrentUser = Depends(require_manager),
    db: Session = Depends(get_db),
):
    req = db.get(WfhRequest, wfh_id)
    if req is None:
        raise HTTPException(status_code=404, detail="WFH request not found")
    if req.status != "pending":
        raise HTTPException(status_code=409, detail="WFH request already reviewed")

    if payload.approve:
        employee = get_employee_or_404(db, req.employee_id)
        if not wfh_service.can_approve(
            db.query(WfhRequest)
            .filter(WfhRequest.employee_id == req.employee_id, WfhRequest.status == "approved")
            .all(),
            req.date_from,
            req.date_to,
            employee.wfh_limit,
        ):
            raise HTTPException(
                status_code=400,
                detail=f"WFH request exceeds monthly limit ({employee.wfh_limit} days).",
            )

    req.reviewed_by = user.employee_id
    req.review_date = datetime.now(UTC)
    req.comment = payload.comment
    req.status = "approved" if payload.approve else "rejected"
    db.commit()
    db.refresh(req)
    return req
