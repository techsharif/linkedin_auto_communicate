import json

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import BotTask, BotTaskStatus, BotTaskType
from connector.models import TaskQueue, Search
from messenger.models import Campaign, ChatMessage


class Command(BaseCommand):
    help = 'collect_search : it will process all pending search results'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.check_or_add_search_task()
        self.check_or_add_connect_campaign_task()
        self.check_or_add_message_campaign_task()

    def check_or_add_search_task(self):
        pending_task_list = BotTask.objects.exclude(status__in=[BotTaskStatus.DONE, BotTaskStatus.ERROR],
                                                    task_type=BotTaskType.SEARCH)
        for pending_task in pending_task_list:
            search = Search.objects.get(id=pending_task.search_id())
            queue_type = ContentType.objects.get_for_model(search)
            task_queue = TaskQueue.objects.filter(object_id=search.id, queue_type=queue_type)
            if task_queue:
                task = task_queue[0]
                pending_task.status = task.status
                pending_task.save()
            else:
                search = Search.objects.get(id=pending_task.extra_id)
                TaskQueue(content_object=search, owner=pending_task.owner).save()

    def check_or_add_connect_campaign_task(self):
        connect_campaigns = Campaign.objects.filter(status=True, is_bulk=False)
        for connect_campaign in connect_campaigns:
            if connect_campaign.owner.is_now_campaign_active():
                queue_type = ContentType.objects.get_for_model(connect_campaign)
                task_queue = TaskQueue.objects.filter(object_id=connect_campaign.id, queue_type=queue_type)
                contacts = connect_campaign.contacts.all()
                if task_queue:
                    for contact in contacts:
                        message = connect_campaign.connection_message.format(Name=contact.name, FirstName=contact.first_name(),
                                                                          Company=contact.company, Title=contact.title)
                        chat_message = ChatMessage(owner=connect_campaign.owner, contact=contact, campaign=connect_campaign,
                                                   text=message, time=timezone.now())
                        chat_message.save()
                        bottask, _ = BotTask.objects.get_or_create(owner=connect_campaign.owner,
                                                                   task_type=BotTaskType.CHECKCONNECT,
                                                                   extra_id=chat_message.id, name=BotTaskType.CHECKCONNECT,
                                                                   )

                else:
                    TaskQueue(owner=connect_campaign.owner, content_object=connect_campaign).save()
                    for contact in contacts:
                        message = connect_campaign.connection_message.format(Name=contact.name,
                                                                          FirstName=contact.first_name(),
                                                                          Company=contact.company, Title=contact.title)
                        chat_message = ChatMessage(owner=connect_campaign.owner, contact=contact,
                                                   campaign=connect_campaign,
                                                   text=message, time=timezone.now())
                        chat_message.save()
                        bottask, _ = BotTask.objects.get_or_create(owner=connect_campaign.owner,
                                                                   task_type=BotTaskType.POSTCONNECT,
                                                                   extra_id=chat_message.id,
                                                                   name=BotTaskType.POSTCONNECT,
                                                                   )
                        bottask.status = BotTaskStatus.QUEUED
                        bottask.save()

    def check_or_add_message_campaign_task(self):
        connect_campaigns = Campaign.objects.filter(status=True, is_bulk=True)
        for connect_campaign in connect_campaigns:
            queue_type = ContentType.objects.get_for_model(connect_campaign)
            task_queue = TaskQueue.objects.filter(object_id=connect_campaign.id, queue_type=queue_type)
            contacts = connect_campaign.contacts.all()
            if task_queue:
                for contact in contacts:
                    message = connect_campaign.welcome_message.format(Name=contact.name, FirstName=contact.first_name(),
                                                                      Company=contact.company, Title=contact.title)
                    chat_message = ChatMessage(owner=connect_campaign.owner, contact=contact, campaign=connect_campaign,
                                               text=message, time=timezone.now())
                    chat_message.save()
                    bottask, _ = BotTask.objects.get_or_create(owner=connect_campaign.owner,
                                                               task_type=BotTaskType.CHECKMESSAGE,
                                                               extra_id=chat_message.id, name=BotTaskType.CHECKMESSAGE,
                                                               )

            else:
                TaskQueue(owner=connect_campaign.owner, content_object=connect_campaign).save()
                for contact in contacts:
                    message = connect_campaign.welcome_message.format(Name=contact.name, FirstName=contact.first_name(),
                                                                      Company=contact.company, Title=contact.title)
                    chat_message = ChatMessage(owner=connect_campaign.owner, contact=contact, campaign=connect_campaign,
                                               text=message, time=timezone.now())
                    chat_message.save()
                    bottask, _ = BotTask.objects.get_or_create(owner=connect_campaign.owner,
                                                               task_type=BotTaskType.POSTMESSAGE,
                                                               extra_id=chat_message.id, name=BotTaskType.POSTMESSAGE,
                                                               )
                    bottask.status = BotTaskStatus.QUEUED
                    bottask.save()
