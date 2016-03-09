# -*- coding: utf-8 -*-
import locale
import logging

from django.conf import settings
from django.contrib.auth.models import Group

from apps.authentication.models import OnlineUser as User
from apps.mommy.registry import Task


class SynchronizeGroups(Task):

    @staticmethod
    def run():
        logger = logging.getLogger('syncer')

        if not hasattr(settings, "GROUP_SYNCER"):
            # Make sure to only run the group syncer if we have the settings for it
            logger.info("GROUP_SYNCER setting not set, not syncing groups")
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.utf8')

            SynchronizeGroups.do_sync(logger)

    @staticmethod
    def do_sync(logger):
        # Loop all the syncs
        for sync in settings.GROUP_SYNCER:
            # Log that syncer we are running
            logger.info('Started: ' + sync.get('name'))

    @staticmethod
    def add_users(sync):
        logger = logging.getLogger(__name__)

        # FORWARD SYNC
        # Syncing users from source groups to destination groups

        # Store number of synced users
        synced = 0

        # Get all users in the source groups
        users_in_source = User.objects.filter(
            groups__id__in=sync.get('source')).exclude(groups__id__in=sync.get('destination'))

        # Check if any users were found
        if len(users_in_source) > 0:
            # Loop all destination groups
            for destination_group in sync.get('destination'):
                # Create object for the current destination group
                destination_group_object = Group.objects.get(id=destination_group)

                # Loop all the users in the source groups
                for user in users_in_source:
                    # Get all groups for the current user
                    user_groups = user.groups.all()

                    # Check if the user has the current destination group
                    if destination_group_object not in user_groups:
                        # User is not in the current destination group, add
                        destination_group_object.user_set.add(user)

                        # Increase syncs
                        synced += 1

            # Check if any changes were made and if there was, log it
            if synced > 0:
                logger.info(str(synced) + ' user(s) were synced to correct destination group(s).')

    @staticmethod
    def remove_users(sync):
        logger = logging.getLogger(__name__)

        # BACKWARDS SYNC
        # Removing users from destination group(s) if they are not in the source group(s)

        # Store number of synced users
        synced = 0

        # Get all users in the destination groups
        users_in_destination = User.objects.filter(
            groups__id__in=sync.get('destination')).all().exclude(groups__id__in=sync.get('source'))

        # Check if any users were found
        if len(users_in_destination) > 0:
            # Loop all the users in the destination groups
            for user in users_in_destination:
                user_in_source_group = False
                user_groups = user.groups.all()

                # Get all groups the user is in
                for user_group in user_groups:
                    # Check if the current user group is in the source list
                    if user_group.id in sync.get('source'):
                        # User group was found
                        user_in_source_group = True

                        # Break out of the loop
                        break

                # Check if user was found in any of the source groups
                if not user_in_source_group:
                    # User was not found, remove from all destination groups
                    for user_group in user_groups:
                        # Check if current group is in destination groups
                        if user_group.id in sync.get('destination'):
                            # This group is a destination group, remove it from the user
                            destination_group = Group.objects.filter(id=user_group.id).first()
                            destination_group.user_set.remove(user)

                            # Increase syncs
                            synced += 1

            # Check if any changes were made and if there was, log it
            if synced > 0:
                logger.info(
                    str(synced) +
                    ' user(s) were removed from the destination group(s) ' +
                    ' because they were not in the source group(s).'
                )
