from background_task import background
from datetime import date
from .models import Project

@background(schedule=60*60*24)  # Schedule to run every 24 hours
def increment_duration_spent():
    today = date.today()
    ongoing_projects = Project.objects.filter(status="In Progress")

    for project in ongoing_projects:
        if project.total_duration > project.duration_spent:
            project.duration_spent += 1
            project.save()
