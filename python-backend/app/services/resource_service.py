"""Resource domain service — outsourced personnel, attendance, settlement, skills."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import BusinessError, ResourceNotFoundError, ValidationError
from app.models.resource.models import (
    AttendanceRecord,
    LeaveRequest,
    OutsourcePerson,
    PerformanceEval,
    PersonnelReplacement,
    PoolMembership,
    PoolPosition,
    ResourcePool,
    Settlement,
    SkillProfile,
)
from app.services.base import BaseService


class ResourceService:
    """Encapsulates all resource-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._person_svc = BaseService(db, OutsourcePerson)
        self._attendance_svc = BaseService(db, AttendanceRecord)
        self._settlement_svc = BaseService(db, Settlement)
        self._skill_svc = BaseService(db, SkillProfile)
        self._leave_svc = BaseService(db, LeaveRequest)
        self._replacement_svc = BaseService(db, PersonnelReplacement)
        self._perf_svc = BaseService(db, PerformanceEval)
        self._position_svc = BaseService(db, PoolPosition)
        self._pool_svc = BaseService(db, ResourcePool)

    # ═══════════════════════════════════════════════════════════════════════
    # OutsourcePerson
    # ═══════════════════════════════════════════════════════════════════════

    async def list_persons(
        self,
        page: int = 1,
        size: int = 10,
        skills: str | None = None,
        status: int | None = None,
        pool_id: str | None = None,
        keyword: str | None = None,
    ) -> PageResult:
        base = select(OutsourcePerson)
        conditions: list = []
        if status is not None:
            conditions.append(OutsourcePerson.pool_status == status)
        if skills:
            conditions.append(OutsourcePerson.skill_tags.ilike(f"%{skills}%"))
        if keyword:
            conditions.append(
                OutsourcePerson.name.ilike(f"%{keyword}%")
                | OutsourcePerson.emp_code.ilike(f"%{keyword}%")
            )
        if pool_id:
            member_stmt = select(PoolMembership.person_id).where(
                PoolMembership.pool_id == pool_id, PoolMembership.status == 1
            )
            member_result = await self.db.execute(member_stmt)
            person_ids = [row[0] for row in member_result.all()]
            if person_ids:
                conditions.append(OutsourcePerson.person_id.in_(person_ids))
            else:
                return PageResult(total=0, page=page, size=size, records=[])

        if conditions:
            base = base.where(*conditions)

        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0

        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(OutsourcePerson.create_time.desc())
        )
        records = [_person_to_dict(p) for p in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def get_person(self, person_id: str) -> dict:
        p = await self._person_svc.get_or_404(person_id)
        return _person_to_dict(p)

    async def create_person(self, req: dict) -> dict:
        person = OutsourcePerson(
            person_id=str(uuid.uuid4()),
            emp_code=req["emp_code"],
            name=req["name"],
            id_card=req.get("id_card", ""),
            phone=req.get("phone"),
            email=req.get("email"),
            skill_tags=req.get("skill_tags"),
            level=req.get("level", 1),
            daily_rate=req.get("daily_rate", Decimal("0")),
            department=req.get("department"),
            pool_status=req.get("pool_status", 0),
            entry_date=req.get("entry_date"),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(person)
        await self.db.flush()
        return {"personId": person.person_id}

    async def update_person(self, person_id: str, updates: dict) -> None:
        await self._person_svc.update(person_id, **updates)

    async def delete_person(self, person_id: str) -> None:
        await self._person_svc.delete(person_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Attendance
    # ═══════════════════════════════════════════════════════════════════════

    async def list_attendance(
        self, person_id: str | None = None, page: int = 1, size: int = 10
    ) -> PageResult:
        base = select(AttendanceRecord)
        if person_id:
            base = base.where(AttendanceRecord.person_id == person_id)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(AttendanceRecord.date.desc())
        )
        records = [_attendance_to_dict(a) for a in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def check_in(self, person_id: str, req: dict) -> dict:
        today = date.today()
        existing = await self.db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.person_id == person_id,
                AttendanceRecord.date == today,
            )
        )
        record = existing.scalar_one_or_none()
        if record:
            if record.check_in_time:
                raise BusinessError(code="DUPLICATE", message="今日已签到")
            record.check_in_time = datetime.now(timezone.utc)
            record.gps_lat = req.get("gps_lat")
            record.gps_lng = req.get("gps_lng")
            record.wifi_mac = req.get("wifi_mac")
        else:
            record = AttendanceRecord(
                attendance_id=str(uuid.uuid4()),
                person_id=person_id,
                date=today,
                check_in_time=datetime.now(timezone.utc),
                gps_lat=req.get("gps_lat"),
                gps_lng=req.get("gps_lng"),
                wifi_mac=req.get("wifi_mac"),
                status=0,
                project_id=req.get("project_id"),
                create_time=datetime.now(timezone.utc),
            )
            self.db.add(record)
        await self.db.flush()
        return {"attendanceId": record.attendance_id, "checkedIn": True}

    async def check_out(self, person_id: str) -> dict:
        today = date.today()
        result = await self.db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.person_id == person_id,
                AttendanceRecord.date == today,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise ResourceNotFoundError("考勤记录", f"{person_id}/{today}")
        record.check_out_time = datetime.now(timezone.utc)
        await self.db.flush()
        return {"attendanceId": record.attendance_id, "checkedOut": True}

    async def get_calendar(self, person_id: str, year: int, month: int) -> list[dict]:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        stmt = (
            select(AttendanceRecord)
            .where(
                AttendanceRecord.person_id == person_id,
                AttendanceRecord.date >= start,
                AttendanceRecord.date < end,
            )
            .order_by(AttendanceRecord.date)
        )
        result = await self.db.execute(stmt)
        return [_attendance_to_dict(a) for a in result.scalars().all()]

    async def create_attendance(self, req: dict) -> dict:
        a = AttendanceRecord(
            attendance_id=str(uuid.uuid4()),
            person_id=req["person_id"],
            date=req["date"],
            check_in_time=req.get("check_in_time"),
            check_out_time=req.get("check_out_time"),
            status=req.get("status", 0),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(a)
        await self.db.flush()
        return {"attendanceId": a.attendance_id}

    async def update_attendance(self, attendance_id: str, updates: dict) -> None:
        await self._attendance_svc.update(attendance_id, **updates)

    async def delete_attendance(self, attendance_id: str) -> None:
        await self._attendance_svc.delete(attendance_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Settlement
    # ═══════════════════════════════════════════════════════════════════════

    async def list_settlements(
        self, person_id: str | None = None, page: int = 1, size: int = 10
    ) -> PageResult:
        base = select(Settlement)
        if person_id:
            base = base.where(Settlement.person_id == person_id)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(Settlement.period.desc())
        )
        records = [_settlement_to_dict(s) for s in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def get_settlement(self, settlement_id: str) -> dict:
        s = await self._settlement_svc.get_or_404(settlement_id)
        return _settlement_to_dict(s)

    async def create_settlement(self, req: dict) -> dict:
        s = Settlement(
            settlement_id=str(uuid.uuid4()),
            person_id=req["person_id"],
            period=req.get("period"),
            daily_rate=req.get("daily_rate"),
            valid_hours=req.get("valid_hours"),
            standard_hours=req.get("standard_hours"),
            total_amount=req.get("total_amount"),
            status=req.get("status", 0),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(s)
        await self.db.flush()
        return {"settlementId": s.settlement_id}

    async def update_settlement(self, settlement_id: str, updates: dict) -> None:
        await self._settlement_svc.update(settlement_id, **updates)

    async def delete_settlement(self, settlement_id: str) -> None:
        await self._settlement_svc.delete(settlement_id)

    async def generate_settlement(self, person_id: str, year: int, month: int) -> dict:
        """Calculate settlement based on attendance hours * daily rate."""
        person = await self._person_svc.get_or_404(person_id)
        period = f"{year:04d}-{month:02d}"

        # Check for existing settlement in this period
        existing = await self.db.execute(
            select(Settlement).where(
                Settlement.person_id == person_id,
                Settlement.period == period,
            )
        )
        if existing.scalar_one_or_none():
            raise BusinessError(code="DUPLICATE", message=f"{period} 的结算已存在")

        # Sum working hours from timesheet (via attendance-based calculation)
        timesheet_hours = await self._get_timesheet_hours(person_id, year, month)

        # Standard monthly hours (22 working days * 8h = 176)
        standard_hours = Decimal("176.0")

        # Overtime calculation
        overtime_hours = max(Decimal("0"), timesheet_hours - standard_hours)
        overtime_fee = overtime_hours * (person.daily_rate * Decimal("1.5") / Decimal("8"))

        # Regular amount
        regular_hours = min(timesheet_hours, standard_hours)
        total = regular_hours * (person.daily_rate / Decimal("8")) + overtime_fee

        settlement = Settlement(
            settlement_id=str(uuid.uuid4()),
            person_id=person_id,
            period=period,
            valid_hours=timesheet_hours,
            standard_hours=standard_hours,
            daily_rate=person.daily_rate,
            performance_coeff=Decimal("1.0"),
            overtime_hours=overtime_hours,
            overtime_fee=overtime_fee,
            total_amount=total,
            status=0,
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(settlement)
        await self.db.flush()
        return _settlement_to_dict(settlement)

    # ═══════════════════════════════════════════════════════════════════════
    # Skills
    # ═══════════════════════════════════════════════════════════════════════

    async def list_skills(self, person_id: str | None = None) -> list[dict]:
        base = select(SkillProfile)
        if person_id:
            base = base.where(SkillProfile.person_id == person_id)
        result = await self.db.execute(base)
        return [_skill_to_dict(s) for s in result.scalars().all()]

    async def create_skill(self, req: dict) -> dict:
        skill = SkillProfile(
            skill_id=str(uuid.uuid4()),
            person_id=req["person_id"],
            skill_name=req["skill_name"],
            proficiency=req.get("proficiency", 1),
            cert_name=req.get("cert_name"),
            cert_date=req.get("cert_date"),
            expiry_date=req.get("expiry_date"),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(skill)
        await self.db.flush()
        return {"skillId": skill.skill_id}

    async def update_skill(self, skill_id: str, updates: dict) -> None:
        await self._skill_svc.update(skill_id, **updates)

    async def delete_skill(self, skill_id: str) -> None:
        await self._skill_svc.delete(skill_id)

    async def match_candidates(self, position_id: str) -> list[dict]:
        """Match persons whose skills fit the position requirements."""
        position = await self._position_svc.get_or_404(position_id)
        req_tags: list[str] = []
        if position.skill_requirements:
            import json
            try:
                req_tags = json.loads(position.skill_requirements)
            except (json.JSONDecodeError, TypeError):
                req_tags = []

        # Fetch all available persons with matching levels
        stmt = select(OutsourcePerson).where(
            OutsourcePerson.pool_status == 0,
            OutsourcePerson.level >= position.level,
        )
        result = await self.db.execute(stmt)
        persons = result.scalars().all()

        candidates: list[dict] = []
        for person in persons:
            person_tags: list[str] = []
            if person.skill_tags:
                import json
                try:
                    person_tags = json.loads(person.skill_tags)
                except (json.JSONDecodeError, TypeError):
                    person_tags = person.skill_tags.split(",") if person.skill_tags else []

            matched = set(req_tags) & set(t.strip() for t in person_tags)
            score = len(matched) / len(req_tags) if req_tags else 0.5
            candidates.append({
                "personId": person.person_id,
                "name": person.name,
                "empCode": person.emp_code,
                "level": person.level,
                "dailyRate": float(person.daily_rate),
                "skills": person_tags,
                "matchScore": round(score, 2),
            })

        candidates.sort(key=lambda c: c["matchScore"], reverse=True)
        return candidates

    # ═══════════════════════════════════════════════════════════════════════
    # LeaveRequest
    # ═══════════════════════════════════════════════════════════════════════

    async def list_leaves(
        self, person_id: str | None = None, page: int = 1, size: int = 10
    ) -> PageResult:
        base = select(LeaveRequest)
        if person_id:
            base = base.where(LeaveRequest.person_id == person_id)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(LeaveRequest.create_time.desc())
        )
        records = [_leave_to_dict(l) for l in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def create_leave(self, req: dict) -> dict:
        leave = LeaveRequest(
            leave_id=str(uuid.uuid4()),
            person_id=req["person_id"],
            leave_type=req.get("leave_type"),
            start_date=req.get("start_date"),
            end_date=req.get("end_date"),
            days=req.get("days"),
            reason=req.get("reason"),
            status="pending",
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(leave)
        await self.db.flush()
        return {"leaveId": leave.leave_id}

    async def approve_leave(self, leave_id: str, approver_id: str) -> dict:
        leave = await self._leave_svc.get_or_404(leave_id)
        if leave.status != "pending":
            raise BusinessError(code="STATUS_ERROR", message="该申请已处理")
        leave.status = "approved"
        leave.approver_id = approver_id
        await self.db.flush()
        return {"leaveId": leave_id, "status": "approved"}

    async def reject_leave(self, leave_id: str, approver_id: str) -> dict:
        leave = await self._leave_svc.get_or_404(leave_id)
        if leave.status != "pending":
            raise BusinessError(code="STATUS_ERROR", message="该申请已处理")
        leave.status = "rejected"
        leave.approver_id = approver_id
        await self.db.flush()
        return {"leaveId": leave_id, "status": "rejected"}

    async def update_leave(self, leave_id: str, updates: dict) -> None:
        await self._leave_svc.update(leave_id, **updates)

    async def delete_leave(self, leave_id: str) -> None:
        await self._leave_svc.delete(leave_id)

    # ═══════════════════════════════════════════════════════════════════════
    # PersonnelReplacement
    # ═══════════════════════════════════════════════════════════════════════

    async def list_replacements(
        self, page: int = 1, size: int = 10
    ) -> PageResult:
        return await self._replacement_svc.list_page(page=page, limit=size)

    async def create_replacement(self, req: dict) -> dict:
        r = PersonnelReplacement(
            replace_id=str(uuid.uuid4()),
            person_id=req["person_id"],
            project_id=req["project_id"],
            reason=req.get("reason"),
            status=req.get("status", "pending"),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(r)
        await self.db.flush()
        return {"replaceId": r.replace_id}

    async def update_replacement(self, replace_id: str, updates: dict) -> None:
        await self._replacement_svc.update(replace_id, **updates)

    async def delete_replacement(self, replace_id: str) -> None:
        await self._replacement_svc.delete(replace_id)

    # ═══════════════════════════════════════════════════════════════════════
    # PerformanceEval
    # ═══════════════════════════════════════════════════════════════════════

    async def list_evals(
        self, person_id: str | None = None, page: int = 1, size: int = 10
    ) -> PageResult:
        base = select(PerformanceEval)
        if person_id:
            base = base.where(PerformanceEval.person_id == person_id)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(PerformanceEval.create_time.desc())
        )
        records = [_eval_to_dict(e) for e in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def get_eval(self, eval_id: str) -> dict:
        e = await self._perf_svc.get_or_404(eval_id)
        return _eval_to_dict(e)

    async def create_eval(self, req: dict) -> dict:
        eval_obj = PerformanceEval(
            eval_id=str(uuid.uuid4()),
            person_id=req["person_id"],
            project_id=req.get("project_id"),
            period=req.get("period"),
            pm_satisfaction=req.get("pm_satisfaction"),
            timesheet_compliance=req.get("timesheet_compliance"),
            task_completion=req.get("task_completion"),
            quality_metric=req.get("quality_metric"),
            attendance_compliance=req.get("attendance_compliance"),
            evaluator_id=req.get("evaluator_id"),
            comments=req.get("comments"),
            create_time=datetime.now(timezone.utc),
        )
        # Compute overall score and grade
        overall = (
            (Decimal(str(req.get("pm_satisfaction", 0))) * Decimal("0.4"))
            + (Decimal(str(req.get("timesheet_compliance", 0))) * Decimal("0.2"))
            + (Decimal(str(req.get("task_completion", 0))) * Decimal("0.2"))
            + (Decimal(str(req.get("quality_metric", 0))) * Decimal("0.1"))
            + (Decimal(str(req.get("attendance_compliance", 0))) * Decimal("0.1"))
        )
        eval_obj.overall_score = overall
        if overall >= Decimal("90"):
            eval_obj.grade = "A"
        elif overall >= Decimal("75"):
            eval_obj.grade = "B"
        elif overall >= Decimal("60"):
            eval_obj.grade = "C"
        else:
            eval_obj.grade = "D"
        self.db.add(eval_obj)
        await self.db.flush()
        return {"evalId": eval_obj.eval_id}

    async def update_eval(self, eval_id: str, updates: dict) -> None:
        await self._perf_svc.update(eval_id, **updates)

    async def delete_eval(self, eval_id: str) -> None:
        await self._perf_svc.delete(eval_id)

    async def get_eval_history(self, person_id: str) -> list[dict]:
        stmt = (
            select(PerformanceEval)
            .where(PerformanceEval.person_id == person_id)
            .order_by(PerformanceEval.create_time.desc())
        )
        result = await self.db.execute(stmt)
        return [_eval_to_dict(e) for e in result.scalars().all()]

    # ═══════════════════════════════════════════════════════════════════════
    # PoolPosition
    # ═══════════════════════════════════════════════════════════════════════

    async def list_positions(
        self, pool_id: str | None = None, page: int = 1, size: int = 10
    ) -> PageResult:
        base = select(PoolPosition)
        if pool_id:
            base = base.where(PoolPosition.pool_id == pool_id)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(PoolPosition.create_time.desc())
        )
        records = [_position_to_dict(p) for p in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def create_position(self, req: dict) -> dict:
        pos = PoolPosition(
            position_id=str(uuid.uuid4()),
            pool_id=req["pool_id"],
            position_name=req["position_name"],
            level=req.get("level", 1),
            skill_requirements=req.get("skill_requirements"),
            head_count=req.get("head_count", 1),
            department=req.get("department"),
            status=req.get("status", 1),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(pos)
        await self.db.flush()
        return {"positionId": pos.position_id}

    async def update_position(self, position_id: str, updates: dict) -> None:
        await self._position_svc.update(position_id, **updates)

    async def delete_position(self, position_id: str) -> None:
        await self._position_svc.delete(position_id)

    # ═══════════════════════════════════════════════════════════════════════
    # ResourcePool
    # ═══════════════════════════════════════════════════════════════════════

    async def list_pools(self, page: int = 1, size: int = 10) -> PageResult:
        return await self._pool_svc.list_page(page=page, limit=size)

    async def get_pool(self, pool_id: str) -> dict:
        pool = await self._pool_svc.get_or_404(pool_id)
        return {
            "poolId": pool.pool_id,
            "poolName": pool.pool_name,
            "managerId": pool.manager_id,
            "description": pool.description,
        }

    async def create_pool(self, req: dict) -> dict:
        pool = ResourcePool(
            pool_id=str(uuid.uuid4()),
            pool_name=req["pool_name"],
            manager_id=req.get("manager_id"),
            description=req.get("description"),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(pool)
        await self.db.flush()
        return {"poolId": pool.pool_id}

    async def update_pool(self, pool_id: str, updates: dict) -> None:
        await self._pool_svc.update(pool_id, **updates)

    async def delete_pool(self, pool_id: str) -> None:
        await self._pool_svc.delete(pool_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Reports
    # ═══════════════════════════════════════════════════════════════════════

    async def utilization_warnings(self) -> list[dict]:
        """Return persons with <50% or >100% utilization."""
        persons_result = await self.db.execute(
            select(OutsourcePerson).where(OutsourcePerson.pool_status == 1)
        )
        persons = persons_result.scalars().all()
        warnings: list[dict] = []
        for person in persons:
            stmt = select(func.sum(Settlement.valid_hours)).where(
                Settlement.person_id == person.person_id,
                Settlement.valid_hours.isnot(None),
            )
            total_hours = (await self.db.execute(stmt)).scalar() or Decimal("0")
            std = Decimal("176.0")
            util = float(total_hours / std) if std > 0 else 0
            if util < 0.5 or util > 1.0:
                warnings.append({
                    "personId": person.person_id,
                    "name": person.name,
                    "empCode": person.emp_code,
                    "utilization": round(util * 100, 1),
                    "status": "under" if util < 0.5 else "over",
                    "totalHours": float(total_hours),
                })
        return warnings

    async def efficiency_report(self, start_date: date, end_date: date) -> dict:
        """Aggregate efficiency metrics for the given period."""
        base = select(func.count(PerformanceEval.eval_id)).where(
            PerformanceEval.create_time >= start_date,
            PerformanceEval.create_time <= end_date,
        )
        total_count = (await self.db.execute(base)).scalar() or 0

        avg_score = (await self.db.execute(
            select(func.avg(PerformanceEval.overall_score)).where(
                PerformanceEval.create_time >= start_date,
                PerformanceEval.create_time <= end_date,
            )
        )).scalar()

        grade_dist = await self.db.execute(
            select(
                PerformanceEval.grade,
                func.count(PerformanceEval.eval_id),
            ).where(
                PerformanceEval.create_time >= start_date,
                PerformanceEval.create_time <= end_date,
            ).group_by(PerformanceEval.grade)
        )
        grades = {row[0]: row[1] for row in grade_dist.all() if row[0]}

        attendance_ok = (await self.db.execute(
            select(func.count(AttendanceRecord.attendance_id)).where(
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date,
                AttendanceRecord.status == 0,
            )
        )).scalar() or 0

        attendance_total = (await self.db.execute(
            select(func.count(AttendanceRecord.attendance_id)).where(
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date,
            )
        )).scalar() or 1

        return {
            "period": {"start": str(start_date), "end": str(end_date)},
            "evalCount": total_count,
            "avgScore": float(avg_score) if avg_score else None,
            "gradeDistribution": grades,
            "attendanceRate": round(attendance_ok / attendance_total * 100, 1),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════════

    async def _get_timesheet_hours(self, person_id: str, year: int, month: int) -> Decimal:
        """Try to get hours from timesheet module; fall back to attendance-based calc."""
        try:
            from app.models.timesheet.models import Timesheet
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, month + 1, 1)
            stmt = select(func.sum(Timesheet.hours_spent)).where(
                Timesheet.user_id == person_id,
                Timesheet.recorded_date >= start,
                Timesheet.recorded_date < end,
            )
            hours = (await self.db.execute(stmt)).scalar()
            return Decimal(str(hours)) if hours else Decimal("0")
        except Exception:
            # Fall back: count attendance days * 8
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, month + 1, 1)
            stmt = select(func.count(AttendanceRecord.attendance_id)).where(
                AttendanceRecord.person_id == person_id,
                AttendanceRecord.date >= start,
                AttendanceRecord.date < end,
            )
            days = (await self.db.execute(stmt)).scalar() or 0
            return Decimal(str(days * 8))


# ═══════════════════════════════════════════════════════════════════════════
# Dict converters
# ═══════════════════════════════════════════════════════════════════════════

def _person_to_dict(p: OutsourcePerson) -> dict:
    return {
        "personId": p.person_id,
        "empCode": p.emp_code,
        "name": p.name,
        "phone": p.phone,
        "email": p.email,
        "skillTags": p.skill_tags,
        "level": p.level,
        "dailyRate": float(p.daily_rate) if p.daily_rate else None,
        "department": p.department,
        "poolStatus": p.pool_status,
        "currentProject": p.current_project,
        "entryDate": str(p.entry_date) if p.entry_date else None,
        "exitDate": str(p.exit_date) if p.exit_date else None,
    }


def _attendance_to_dict(a: AttendanceRecord) -> dict:
    return {
        "attendanceId": a.attendance_id,
        "personId": a.person_id,
        "date": str(a.date) if a.date else None,
        "checkInTime": str(a.check_in_time) if a.check_in_time else None,
        "checkOutTime": str(a.check_out_time) if a.check_out_time else None,
        "gpsLat": float(a.gps_lat) if a.gps_lat else None,
        "gpsLng": float(a.gps_lng) if a.gps_lng else None,
        "status": a.status,
    }


def _settlement_to_dict(s: Settlement) -> dict:
    return {
        "settlementId": s.settlement_id,
        "personId": s.person_id,
        "period": s.period,
        "validHours": float(s.valid_hours) if s.valid_hours else None,
        "standardHours": float(s.standard_hours) if s.standard_hours else None,
        "dailyRate": float(s.daily_rate) if s.daily_rate else None,
        "performanceCoeff": float(s.performance_coeff) if s.performance_coeff else None,
        "overtimeHours": float(s.overtime_hours) if s.overtime_hours else None,
        "overtimeFee": float(s.overtime_fee) if s.overtime_fee else None,
        "totalAmount": float(s.total_amount) if s.total_amount else None,
        "status": s.status,
    }


def _skill_to_dict(s: SkillProfile) -> dict:
    return {
        "skillId": s.skill_id,
        "personId": s.person_id,
        "skillName": s.skill_name,
        "proficiency": s.proficiency,
        "certName": s.cert_name,
        "certDate": str(s.cert_date) if s.cert_date else None,
        "expiryDate": str(s.expiry_date) if s.expiry_date else None,
    }


def _leave_to_dict(l: LeaveRequest) -> dict:
    return {
        "leaveId": l.leave_id,
        "personId": l.person_id,
        "leaveType": l.leave_type,
        "startDate": str(l.start_date) if l.start_date else None,
        "endDate": str(l.end_date) if l.end_date else None,
        "days": l.days,
        "reason": l.reason,
        "status": l.status,
        "approverId": l.approver_id,
    }


def _eval_to_dict(e: PerformanceEval) -> dict:
    return {
        "evalId": e.eval_id,
        "personId": e.person_id,
        "projectId": e.project_id,
        "period": e.period,
        "pmSatisfaction": float(e.pm_satisfaction) if e.pm_satisfaction else None,
        "timesheetCompliance": float(e.timesheet_compliance) if e.timesheet_compliance else None,
        "taskCompletion": float(e.task_completion) if e.task_completion else None,
        "qualityMetric": float(e.quality_metric) if e.quality_metric else None,
        "attendanceCompliance": float(e.attendance_compliance) if e.attendance_compliance else None,
        "overallScore": float(e.overall_score) if e.overall_score else None,
        "grade": e.grade,
        "evaluatorId": e.evaluator_id,
        "comments": e.comments,
    }


def _position_to_dict(p: PoolPosition) -> dict:
    return {
        "positionId": p.position_id,
        "poolId": p.pool_id,
        "positionName": p.position_name,
        "level": p.level,
        "skillRequirements": p.skill_requirements,
        "headCount": p.head_count,
        "filledCount": p.filled_count,
        "department": p.department,
        "status": p.status,
    }
