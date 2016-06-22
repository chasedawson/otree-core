#!/usr/bin/env python
# -*- coding: utf-8 -*-

from otree_save_the_change.mixins import SaveTheChange

from otree.db import models
from otree.common_internal import get_models_module
from otree.models.fieldchecks import ensure_field
import django.core.exceptions


class BaseGroup(SaveTheChange, models.Model):
    """Base class for all Groups.
    """

    class Meta:
        abstract = True
        index_together = ['session', 'id_in_subsession']
        ordering = ['pk']

    _is_missing_players = models.BooleanField(default=False, db_index=True)

    id_in_subsession = models.PositiveIntegerField(db_index=True)

    def __unicode__(self):
        return str(self.pk)

    def get_players(self):
        return list(self.player_set.order_by('id_in_group'))

    def get_player_by_id(self, id_in_group):
        try:
            return self.player_set.get(id_in_group=id_in_group)
        except django.core.exceptions.ObjectDoesNotExist:
            raise ValueError(
                'No player with id_in_group {}'.format(id_in_group))

    def get_player_by_role(self, role):
        for p in self.get_players():
            if p.role() == role:
                return p
        raise ValueError('No player with role {}'.format(role))

    def set_players(self, players_list):
        for i, player in enumerate(players_list, start=1):
            player.group = self
            player.id_in_group = i
            player.save()

    def in_round(self, round_number):
        '''You should not use this method if
        you are rearranging groups between rounds.'''

        return type(self).objects.filter(
            session=self.session,
            id_in_subsession=self.id_in_subsession,
            round_number=round_number,
        )

    def in_rounds(self, first, last):
        '''You should not use this method if
        you are rearranging groups between rounds.'''

        qs = type(self).objects.filter(
            session=self.session,
            id_in_subsession=self.id_in_subsession,
            round_number__range=(first, last),
        ).order_by('round_number')

        ret = list(qs)
        assert len(ret) == last-first+1
        return ret

    def in_previous_rounds(self):
        return self.in_rounds(1, self.round_number-1)

    def in_all_rounds(self):
        return self.in_previous_rounds() + [self]

    @property
    def _Constants(self):
        return get_models_module(self._meta.app_config.name).Constants

    @classmethod
    def _ensure_required_fields(cls):
        """
        Every ``Group`` model requires a foreign key to the ``Subsession``
        model of the same app.
        """
        subsession_model = '{app_label}.Subsession'.format(
            app_label=cls._meta.app_label)
        subsession_field = models.ForeignKey(subsession_model)
        ensure_field(cls, 'subsession', subsession_field)
