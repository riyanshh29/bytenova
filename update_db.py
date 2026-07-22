"""Update the demo candidate's application with correct dates and status."""
import sys
sys.path.insert(0, '.')
from app import create_app, db
from app.models import Application
from datetime import datetime, timezone

app = create_app()
with app.app_context():
    app = Application.query.filter_by(candidate_id=2, job_id=1).first()
    if app:
        app.applied_at = datetime(2026, 5, 16, 10, 0, tzinfo=timezone.utc)
        app.updated_at = datetime(2026, 7, 21, 10, 0, tzinfo=timezone.utc)
        app.status = 'interview'
        db.session.commit()
        print(f'Updated application {app.id}: status={app.status}')
    else:
        print('No application found for candidate_id=2, job_id=1')
    print('Current applications:')
    for a in Application.query.all():
        print(f'  ID={a.id} candidate={a.candidate_id} job={a.job_id} status={a.status} applied={a.applied_at}')
