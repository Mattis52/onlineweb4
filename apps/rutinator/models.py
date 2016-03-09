from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group


User = settings.AUTH_USER_MODEL

class Task(models.Model):
    title = models.CharField(u"Tittel", max_length=45)
    description = models.CharField(u"Beskrivelse", max_length=100)
    completed = models.BooleanField(u"Ferdigstilt", default=False)
    completed_date = models.DateTimeField(u"Ferdigstilt dato", blank=True, null=True)
    deadline = models.DateTimeField(u"Tidsfrist", blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    group = models.ForeignKey(Group)
    task_type = models.IntegerField(choices=(
        (1, 'En gang'),
        (2, 'Gjentagende'),
    ), blank=True, null=True)


def __unicode__(self):
    return self.title
