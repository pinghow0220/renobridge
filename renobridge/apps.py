from django.apps import AppConfig
import sys

class RenobridgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'renobridge'

    def ready(self):
        if 'runserver' in sys.argv or 'process_tasks' in sys.argv:
            from background_task.models import Task
            if not Task.objects.filter(task_name='renobridge.tasks.increment_duration_spent').exists():
                from .tasks import increment_duration_spent
                increment_duration_spent(repeat=60 * 60 * 24)
