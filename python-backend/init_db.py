"""Initialize database: create tables and seed test data."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.database import engine
from app.models.base import Base
# Import all models so they are registered with Base.metadata
from app.models.auth.models import User  # noqa: F401
from app.models.system.models import (  # noqa: F401
    Dept, Role, Permission, Dict, Config, Announcement,
    AuditLog, Meeting, ReviewMeeting, ReviewOpinion, Asset,
)
from app.models.project.models import (  # noqa: F401
    Project, ProjectTask, WbsNode, ProjectRisk, ProjectMilestone,
    ProjectChange, ProjectClose, Sprint, PreInitiation,
    ProgressAlert, CodeRepo, BuildRecord, ProjectDependency,
)
from app.models.business.models import (  # noqa: F401
    Contract, ContractPayment, Customer, Supplier,
    Opportunity, Quotation, ProcurementPlan, ContractInvoice,
)
from app.models.cost.models import Budget, Cost, CostAlert, CostOutsource, ExpenseReimbursement  # noqa: F401
from app.models.resource.models import (  # noqa: F401
    OutsourcePerson, PoolMembership, SkillProfile, AttendanceRecord,
    Settlement, PoolPosition, PerformanceEval, LeaveRequest, PersonnelReplacement,
)
from app.models.timesheet.models import Timesheet, TimesheetAttendance  # noqa: F401
from app.models.knowledge.models import (  # noqa: F401
    KnowledgeDoc, KnowledgeTemplate, KnowledgeReview, ComplianceChecklist,
)
from app.models.notify.models import NotifyMessage, NotifyTemplate, NotifyPreference  # noqa: F401
from app.models.workflow.models import ProcessDefinition, ProcessInstance  # noqa: F401
from app.models.audit.models import AuditLogEntry  # noqa: F401
from app.models.quality.models import QualityDefect, QualityMetric  # noqa: F401
from app.models.file.models import FileInfo  # noqa: F401

from app.core.security import hash_password


async def init_db():
    """Drop and recreate all tables, then seed test data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Seed test data
    from app.database import async_session_factory

    async with async_session_factory() as session:
        # Create default department
        dept = Dept(
            dept_id="1",
            dept_name="技术研发部",
            parent_id=None,
            sort_order=1,
            status=1,
        )
        session.add(dept)

        # Create admin role
        role = Role(
            role_id="1",
            role_name="系统管理员",
            role_code="admin",
            status=1,
        )
        session.add(role)

        # Create admin user (password: Admin123!)
        admin = User(
            user_id="admin-001",
            username="admin",
            password=hash_password("Admin123!"),
            name="系统管理员",
            dept_id="1",
            email="admin@updg.com",
            phone="13800138000",
            status=1,
            password_changed_at=datetime.now(timezone.utc),
        )
        session.add(admin)

        # Link admin user to admin role
        from app.models.auth.models import UserRole
        session.add(UserRole(
            user_id="admin-001",
            role_id="1",
        ))

        # Create test project
        project = Project(
            project_id="proj-001",
            project_name="数字化转型试点项目",
            project_code="DT-2026-001",
            project_type="研发",
            status="active",
            manager_id="admin-001",
            manager_name="系统管理员",
            department_id="1",
            department_name="技术研发部",
            budget=5000000,
            customer="某银行",
            description="数字化转型试点项目",
            progress=35,
        )
        session.add(project)

        await session.commit()

        # ── Seed outsource persons (F-501 ~ F-513) ──────────────
        from app.models.resource.models import PoolMembership, SkillProfile

        persons_data = [
            ("emp-001", "张三", "Java开发", "Java", "高级", 3, 1200, "软件开发组", 1),
            ("emp-002", "李四", "前端开发", "Vue,React", "中级", 2, 1000, "前端组", 0),
            ("emp-003", "王五", "数据分析", "Python,SQL", "高级", 3, 1400, "数据组", 1),
            ("emp-004", "赵六", "测试工程师", "Selenium,JMeter", "中级", 2, 900, "测试组", 0),
            ("emp-005", "陈七", "DevOps", "Docker,K8s", "专家", 4, 1800, "运维组", 1),
            ("emp-006", "孙八", "产品经理", "Axure,PRD", "高级", 3, 1300, "产品组", 0),
            ("emp-007", "周九", "UI设计师", "Figma,Sketch", "中级", 2, 1000, "设计组", 1),
            ("emp-008", "吴十", "DBA", "MySQL,Redis", "高级", 3, 1500, "DBA组", 2),
        ]

        for emp_code, name, role_desc, skill_str, level_name, level, daily_rate, dept, status in persons_data:
            person = OutsourcePerson(
                person_id=str(uuid.uuid4()), emp_code=emp_code, name=name,
                id_card=hash_password(f"ID-{emp_code}"),  # placeholder encrypted
                phone=f"139{str(uuid.uuid4())[:8]}", email=f"{emp_code}@company.com",
                skill_tags=json.dumps([s.strip() for s in skill_str.split(",")]),
                level=level, daily_rate=Decimal(str(daily_rate)),
                department=dept, pool_status=status,
                entry_date=datetime(2025, 6, 1).date() if status == 1 else None,
                background_check=1, security_review=1, confidentiality_agreement=1,
                attendance_group="总行考勤组A" if status == 1 else None,
            )
            session.add(person)

        # Create skill profiles for first 3 persons
        for i, (emp_code, _, _, skill_str, _, _, _, _, _) in enumerate(persons_data[:3]):
            # We need the person_id, let's query it back
            from sqlalchemy import select as _select
            person_stmt = _select(OutsourcePerson).where(OutsourcePerson.emp_code == emp_code)
            person_result = await session.execute(person_stmt)
            person = person_result.scalar_one()

            for skill_name in skill_str.split(","):
                skill = SkillProfile(
                    skill_id=str(uuid.uuid4()), person_id=person.person_id,
                    skill_name=skill_name.strip(), proficiency=3,
                )
                session.add(skill)

        print("  8名外包人员档案已创建")

        await session.commit()
        print("  测试数据已提交")

    print("数据库初始化完成！")
    print("测试账号:")
    print("  用户名: admin")
    print("  密码: Admin123!")


if __name__ == "__main__":
    asyncio.run(init_db())
