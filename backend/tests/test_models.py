from app.models.resume import Bullet, Job, Project, ResumeDoc, Suggestion


def test_resume_doc_collects_all_bullets() -> None:
    job_bullet = Bullet(text="Shipped X", section="experience", parent_id="job-1")
    project_bullet = Bullet(text="Built Y", section="projects", parent_id="proj-1")
    resume = ResumeDoc(
        experience=[Job(id="job-1", company="Acme", title="SWE", bullets=[job_bullet])],
        projects=[Project(id="proj-1", name="Y", bullets=[project_bullet])],
    )
    bullets = resume.all_bullets()
    assert {b.id for b in bullets} == {job_bullet.id, project_bullet.id}


def test_suggestion_default_id_is_unique() -> None:
    s1 = Suggestion(bullet_id="b1", issue="vague", rationale="r", rewrite="x")
    s2 = Suggestion(bullet_id="b1", issue="vague", rationale="r", rewrite="x")
    assert s1.id != s2.id
