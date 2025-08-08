# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Job, CustomUser, Notification

@receiver(post_save, sender=Job)
def create_job_notification(sender, instance, created, **kwargs):
    """
    A signal that creates a notification for all students when a new job is created.
    'instance' is the Job object that was just saved.
    'created' is a boolean that is True if this is a new record.
    """
    if created:
        # Get all users who are students
        students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT)

        # Create the notification message
        message = (
            f"New Opening: {instance.title} at {instance.company}. "
            f"Salary: {instance.currency} {instance.salary_min}-{instance.salary_max}. "
            f"Apply by: {instance.deadline.strftime('%b %d, %Y')}."
        )

        # Create a notification object for each student
        notifications_to_create = [
            Notification(user=student, job=instance, message=message)
            for student in students
        ]
        
        # Use bulk_create for efficiency - it's much faster than creating one by one in a loop
        Notification.objects.bulk_create(notifications_to_create)

        print(f"Created notifications for {len(students)} students for job: {instance.title}")