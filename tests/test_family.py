from datetime import date, datetime, timedelta, timezone

from app.models.curriculum import Grade
from app.models.family import FamilyInvite, ParentProfile, StudentProfile
from app.models.user import User
from app.routers.family import digest_code


def register_and_login(client, email, password="StrongPass123!"):
    response = client.post(
        "/auth/register",
        json={"full_name": email.split("@")[0], "email": email, "password": password},
    )
    assert response.status_code in (201, 200), response.text
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_parent_account(client, db_session, email):
    token = register_and_login(client, email)
    user = db_session.query(User).filter_by(email=email).one()
    user.role = "parent"
    db_session.add(ParentProfile(user_id=user.id, name="Test Parent", phone=None))
    db_session.commit()
    # Registration token contains student role, so re-login to obtain
    # the updated role token.
    token = client.post(
        "/auth/login", json={"email": email, "password": "StrongPass123!"}
    ).json()["access_token"]
    return user.id, token


def create_student_profile(client, db_session, email, grade_id, dob=date(2012, 1, 1)):
    token = register_and_login(client, email)
    user = db_session.query(User).filter_by(email=email).one()
    response = client.post(
        "/profiles/student",
        headers=auth(token),
        json={
            "name": "Student Name",
            "grade_id": str(grade_id),
            "school": "Test School",
            "exam_date": "2027-03-01",
            "preferred_language": "Urdu",
            "date_of_birth": dob.isoformat(),
        },
    )
    assert response.status_code == 201, response.text
    return user.id, token


def create_grade(db_session):
    grade = Grade(name="Test Grade")
    db_session.add(grade)
    db_session.commit()
    db_session.refresh(grade)
    return grade.id


def test_parent_can_link_student_and_read_profile(client, db_session):
    grade_id = create_grade(db_session)
    student_id, student_token = create_student_profile(
        client, db_session, "student1@example.com", grade_id
    )
    parent_id, parent_token = create_parent_account(
        client, db_session, "parent1@example.com"
    )

    invite = client.post("/family/invites", headers=auth(student_token))
    assert invite.status_code == 201, invite.text
    code = invite.json()["code"]
    assert len(code) == 6

    linked = client.post(
        "/family/link", headers=auth(parent_token), json={"code": code}
    )
    assert linked.status_code == 201, linked.text
    assert linked.json()["parent_id"] == parent_id
    assert linked.json()["student_id"] == student_id

    read = client.get(f"/family/children/{student_id}", headers=auth(parent_token))
    assert read.status_code == 200
    assert read.json()["name"] == "Student Name"


def test_unlinked_parent_cannot_read_student(client, db_session):
    grade_id = create_grade(db_session)
    student_id, _ = create_student_profile(
        client, db_session, "student2@example.com", grade_id
    )
    _, parent_token = create_parent_account(client, db_session, "parent2@example.com")
    response = client.get(f"/family/children/{student_id}", headers=auth(parent_token))
    assert response.status_code == 403


def test_expired_invite_rejected(client, db_session):
    grade_id = create_grade(db_session)
    student_id, student_token = create_student_profile(
        client, db_session, "student3@example.com", grade_id
    )
    _, parent_token = create_parent_account(client, db_session, "parent3@example.com")
    invite_response = client.post("/family/invites", headers=auth(student_token))
    code = invite_response.json()["code"]
    invite = (
        db_session.query(FamilyInvite).filter_by(code_digest=digest_code(code)).one()
    )
    invite.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    response = client.post(
        "/family/link", headers=auth(parent_token), json={"code": code}
    )
    assert response.status_code == 400


def test_parent_consent_timestamp_saved(client, db_session):
    grade_id = create_grade(db_session)
    student_id, student_token = create_student_profile(
        client, db_session, "student4@example.com", grade_id
    )
    _, parent_token = create_parent_account(client, db_session, "parent4@example.com")
    code = client.post("/family/invites", headers=auth(student_token)).json()["code"]
    assert (
        client.post(
            "/family/link", headers=auth(parent_token), json={"code": code}
        ).status_code
        == 201
    )
    consent = client.post(
        f"/family/children/{student_id}/consent",
        headers=auth(parent_token),
        json={"consent_given": True},
    )
    assert consent.status_code == 200, consent.text
    profile = db_session.get(StudentProfile, student_id)
    assert profile.parent_consent_given is True
    assert profile.parent_consent_date is not None
    assert profile.consent_parent_id is not None


def test_invite_code_is_single_use(client, db_session):
    grade_id = create_grade(db_session)
    _, student_token = create_student_profile(
        client, db_session, "student5@example.com", grade_id
    )
    _, parent_token = create_parent_account(client, db_session, "parent5@example.com")
    code = client.post("/family/invites", headers=auth(student_token)).json()["code"]
    first = client.post("/family/link", headers=auth(parent_token), json={"code": code})
    assert first.status_code == 201
    second = client.post(
        "/family/link", headers=auth(parent_token), json={"code": code}
    )
    assert second.status_code == 400
