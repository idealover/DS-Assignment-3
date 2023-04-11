from django.db import models

class Topic(models.Model):
    #model for the topic
    topic_name = models.CharField(max_length = 200)
    created = models.DateTimeField(auto_now_add=True)
    partition_number = models.PositiveIntegerField()

    class Meta:
        ordering = ['created']

class Producer(models.Model):
    #Model for the producer
    subscribed_topic = models.ForeignKey(Topic, related_name = 'topic_p',on_delete = models.CASCADE)
    pid = models.PositiveIntegerField()

class LogMessage(models.Model):
    message = models.TextField()
    created = models.DateTimeField(auto_now_add = True)

    topic_name = models.ForeignKey(Topic, related_name = 'topic_name_lm', on_delete = models.CASCADE)

    class Meta:
        ordering = ['created']

class Consumer(models.Model):
    #Model for the consumer
    cid = models.PositiveIntegerField()
    subscriptions = models.ManyToManyField(Topic, through = 'ConsumerSubscriptions')
    views = models.ManyToManyField(LogMessage, through = 'ConsumerViews')

class ConsumerSubscriptions(models.Model):
    #To store which consumer is subscribed to which topic
    subscribed_topic = models.ForeignKey(Topic, related_name = 'subscribed_topic',on_delete = models.CASCADE)
    user = models.ForeignKey(Consumer, related_name = 'user_cs', on_delete = models.CASCADE)

class ConsumerViews(models.Model):
    #To store which consumer viewed which topic
    viewed_log = models.ForeignKey(LogMessage, related_name = 'viewed_log', on_delete = models.CASCADE)
    user = models.ForeignKey(Consumer, related_name = 'user_cv', on_delete = models.CASCADE)

class partitionReplicaData(models.Model):
    topic_m = models.ForeignKey(Topic, related_name = 'topic_name_prd', on_delete = models.CASCADE)
    my_port = models.PositiveIntegerField()
    peer1 = models.PositiveIntegerField()
    peer2 = models.PositiveIntegerField()