from app.application.interfaces.job_repository_interface import IJobRepository
from app.domain.entities import Job
from app.infrastructure.database.mappers.job_mapper import to_domain, to_orm
from app.infrastructure.database.models.job_model import JobORM
from sqlalchemy.ext.asyncio import AsyncSession


class JobRepository(IJobRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job: Job):
        orm = to_orm(job)
        self.session.add(orm)
        await self.session.commit()

    async def get(self, job_id: str):
        result = await self.session.get(JobORM, job_id)
        return to_domain(result) if result else None

    async def update(self, job: Job):
        result = await self.session.get(JobORM, job.id)
        if result:
            result.status = job.status.value
            result.error = job.error
            await self.session.commit()
