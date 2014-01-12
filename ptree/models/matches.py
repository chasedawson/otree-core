from django.db import models
import ptree.sequence_of_experiments.models

class BaseMatch(models.Model):
    """
    Base class for all Matches.
    """

    sequence_of_experiments = models.ForeignKey(ptree.sequence_of_experiments.models.SequenceOfExperiments,
                                                related_name = '%(app_label)s_%(class)s')


    def __unicode__(self):
        return str(self.pk)

    def is_ready_for_next_participant(self):
        """
        Needs to be implemented by child classes.
        Whether the game is ready for another participant to be added.
        """
        raise NotImplementedError()

    def participants(self):
        return self.participant_set.order_by('index_among_participants_in_match')

    class Meta:
        abstract = True
        verbose_name_plural = "matches"
        ordering = ['pk']