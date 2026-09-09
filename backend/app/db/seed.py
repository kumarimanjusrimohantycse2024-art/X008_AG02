from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Job, JobStatus, Requirement, RequirementPriority, User, UserRole


def seed() -> None:
    settings = get_settings()
    if not settings.seed_password_hash and not settings.demo_recruiter_password:
        raise RuntimeError("SEED_PASSWORD_HASH or DEMO_RECRUITER_PASSWORD must be set for seeding.")
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == settings.seed_user_email))
        if user is None:
            password_hash = settings.seed_password_hash or hash_password(settings.demo_recruiter_password or "")
            user = User(email=settings.seed_user_email, password_hash=password_hash, name="TalentScreen Seed User", role=UserRole.RECRUITER)
            session.add(user)
            session.flush()
        job = session.scalar(select(Job).where(Job.title == "Backend Software Engineer", Job.created_by == user.id))
        if job is None:
            job = Job(title="Backend Software Engineer", department="Engineering", description="Build reliable backend services.", status=JobStatus.DRAFT, created_by=user.id)
            job.requirements = [
                Requirement(name="Python backend experience", description="Professional backend development with Python.", priority=RequirementPriority.REQUIRED, weight=1, aliases=["Python"], evidence_expectations={"coursework_insufficient": True}),
                Requirement(name="PostgreSQL experience", description="Practical relational database experience.", priority=RequirementPriority.PREFERRED, weight=0.8, aliases=["Postgres", "PostgreSQL"], evidence_expectations={}),
            ]
            session.add(job)
        if settings.demo_admin_email and settings.demo_admin_password:
            admin = session.scalar(select(User).where(User.email == settings.demo_admin_email.strip().lower()))
            if admin is None:
                session.add(User(email=settings.demo_admin_email.strip().lower(), password_hash=hash_password(settings.demo_admin_password), name="TalentScreen Admin", role=UserRole.ADMIN))
        if settings.demo_recruiter_email and settings.demo_recruiter_password:
            recruiter = session.scalar(select(User).where(User.email == settings.demo_recruiter_email.strip().lower()))
            if recruiter is None:
                session.add(User(email=settings.demo_recruiter_email.strip().lower(), password_hash=hash_password(settings.demo_recruiter_password), name="TalentScreen Recruiter", role=UserRole.RECRUITER))
        session.commit()
    print(f"Seeded development data for {settings.seed_user_email}.")


if __name__ == "__main__":
    seed()
