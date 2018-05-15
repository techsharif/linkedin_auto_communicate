
from django.core import serializers
from django.db import models

from app.models import LinkedInUser


try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ContactStatus(object):
    
    ALL_N = -1 # All
    LATER_N = 200 # Later
    CONNECTED_N = 3 # connected
    CONNECT_REQUESTED_N = 1 # connect requested
    DISCONNECTED_N = 23 # disconeted
    IN_QUEUE_N = 0 # in queue
    LATER_N = 20 # later
    MESSAGE_N = 7 # message - sent message
    NO_INTEREST_N = 21 # no iterested
    OLD_CONNECT_N = 22 # old connect - use this when the contact is first imported
    REPLIED_N = 10 # replie
    TALKING_N = 12 # talking
    TALKING_REPLIED_N = 100 # talking and replied
    WELCOME_MES_N = 6 # sent welcome message
    CONNECT_REQ_N = 5 # connect request
    UNREAD_N = 200 # unread
    
    ALL = 'All'
    LATER = 'Later'
    MESSAGE = 'Message'
    NO_INTEREST = 'No Interest'
    OLD_CONNECT = 'Old Connect'
    REPLIED = 'Replied'
    TALKING = 'Talking'
    TALKING_REPLIED = 'Talking & Replied'
    
    CONNECTED = 'Connected'
    CONNECT_REQUESTED = 'Connect Requested'
    DISCONNECTED = 'Disconnected'
    IN_QUEUE = 'In Queue'
    CONNECT_REQ = 'Connect Req'
    
    WELCOME_MES = 'Welcome Mes'
    UNREAD = 'Unread'
    
    contact_statuses = (
        (ALL_N, ALL),
        (LATER_N, LATER),
        (MESSAGE_N, MESSAGE),
        (NO_INTEREST_N, NO_INTEREST),
        (OLD_CONNECT_N, OLD_CONNECT),
        (REPLIED_N, REPLIED),
        (TALKING_N, TALKING),
        (TALKING_REPLIED_N, TALKING_REPLIED),
        )
    
    IMPORTED = 'Imported'
    CONNECTOR = 'connector'
    MESSENGER = 'messenger'
    
    # connector_messengers = (
    #    (IMPORTED, IMPORTED),
    #    (IN_QUEUE, IN_QUEUE),
    #)
    
    inbox_statuses = (
        (ALL_N, ALL),
        (UNREAD_N, UNREAD),
        (CONNECTED_N, CONNECTED),
        (CONNECT_REQUESTED_N, CONNECT_REQUESTED),
        (DISCONNECTED_N, DISCONNECTED),
        (IN_QUEUE_N, IN_QUEUE),
        (NO_INTEREST_N, NO_INTEREST),        
        (LATER_N, LATER),
        (MESSAGE_N, MESSAGE),        
        (OLD_CONNECT_N, OLD_CONNECT),
        (REPLIED_N, REPLIED),
        (TALKING_N, TALKING),
        (TALKING_REPLIED_N, TALKING_REPLIED),
        (OLD_CONNECT_N, OLD_CONNECT),
        (WELCOME_MES_N, WELCOME_MES),
        )
    
    search_result_statuses = (
        (IN_QUEUE_N, IN_QUEUE),
        (CONNECT_REQ_N, CONNECT_REQ)
        )
    
    CHAT_MSG = 'Chat'
    
    MESSSAGETYPES = (
        (REPLIED_N, REPLIED),
        (TALKING_N, TALKING),
        (TALKING_REPLIED_N, TALKING_REPLIED),
        (CONNECT_REQ_N, CONNECT_REQ)
        )
    
    @staticmethod
    def valid_status(status):
        for n, v in ContactStatus.inbox_statuses:
            if n == status:
                return True
        return False

class CommonContactField(models.Model):
    company = models.CharField(max_length=100, db_index=True, blank=True, 
                               null=True)
    industry = models.CharField(max_length=100, db_index=True, blank=True, 
                                null=True)
    location = models.CharField(max_length=100, db_index=True, blank=True, 
                                null=True)
    title = models.CharField(max_length=100, db_index=True, blank=True, 
                                null=True)
    
    class Meta:
        abstract = True
    
class ContactField(CommonContactField):
    linkedin_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, db_index=True)    
    latest_activity = models.DateTimeField()
    
    class Meta:
        abstract = True

# this is not a real entity, the list inbox with is_connected = True
"""
class Contact(TimeStampedModel, ContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='contacts',
                                on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, 
                              choices=ContactStatus.contact_statues, 
                              default=ContactStatus.OLD_CONNECT)
    notes = models.TextField()

    def __str__(self):
        return force_text(str(self.account_id) + "  " + self.name)

    class Meta():
        abstract = False
        # db_table = 'contacts'
"""

class Campaign(TimeStampedModel):
    owner = models.ForeignKey(LinkedInUser, related_name='messegercampaigns',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=100, db_index=True)
    status = models.BooleanField(default=True)
    contacts = models.ManyToManyField("Inbox", related_name="campaigns")
    copy_campaign = models.ForeignKey('self', on_delete=models.SET_NULL,
                                       blank=True, null=True)
    
    # True is messenger campaign, false is connector campaign
    is_bulk = models.BooleanField(default=False)
    connection_message = models.TextField(max_length=2000, blank=True, null=True)
    welcome_message = models.TextField(max_length=2000, blank=True, null=True)
    welcome_time = models.IntegerField(default=0, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def copy_step_message(self):        
        for cc in self.copy_campaign.campaignsteps.all():
            cc.clone(self)

class CampaignStepField(models.Model):
    step_number = models.IntegerField(db_index=True, default=1)
    step_time = models.IntegerField(blank=True, null=True, default=0)
    message = models.TextField()
    action = models.CharField(max_length=100, db_index=True)
    
    
    class Meta:
        abstract = False
        

class CampaignStep(TimeStampedModel, CampaignStepField):
    campaign = models.ForeignKey(Campaign, related_name='campaignsteps',
                                 on_delete=models.CASCADE)

    class Meta():
        abstract = False
        
    def clone(self, parent):
        self.pk = None
        self.campaign = parent
        self.save()
        
    def __str__(self):
        return "{0} - {1}".format(self.campaign, self.step_time)
    

class MessageField(TimeStampedModel):
    
    text = models.TextField()
    time = models.DateTimeField()
         
    class Meta():
        abstract = True
    
class ChatMessage(MessageField):
    owner = models.ForeignKey(LinkedInUser, related_name='chatmessages',
                              on_delete=models.CASCADE)
    contact = models.ForeignKey("Inbox", related_name='contact_messages',
                               on_delete=models.SET_NULL, null=True)
    type = models.IntegerField(blank=True, 
                            choices=ContactStatus.MESSSAGETYPES,
                            default=ContactStatus.TALKING_N)
    campaign = models.ForeignKey(Campaign, related_name='campaign_messages',
                                  on_delete=models.CASCADE, blank=True,
                                  null=True)
    replied_date = models.DateTimeField(blank=True, null=True)
    replied_other_date = models.DateTimeField(blank=True, null=True)
    
    parent = models.ForeignKey('self', related_name='previous', blank=True,
                               null=True, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=True)
    is_direct = models.BooleanField(default=True)

    class Meta():
        abstract = False
        
class Inbox(ContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='inboxes',
                                on_delete=models.CASCADE)
    status = models.IntegerField(choices=ContactStatus.inbox_statuses, 
                              default=ContactStatus.OLD_CONNECT_N)
    is_connected = models.BooleanField(default=False)
    
    connected_date = models.DateTimeField(blank=True, null=True)
    
    # to save notes at convesation on right
    notes = models.TextField(blank=True, null=True)
    
    class Meta():
        abstract = False
    
    
    def __str__(self):
        return self.name
    
    def detach_from_campaigns(self):
        self.campaigns.clear()
        
    def change_status(self, new_status):
        if self.status != new_status:       
            self.status = new_status
            self.save() 
            
    def attach_to_campaign(self, campaign):
        # detach from other campain
        self.detach_from_campaigns()
        self.change_status(ContactStatus.IN_QUEUE_N)
        campaign.contacts.add(self)