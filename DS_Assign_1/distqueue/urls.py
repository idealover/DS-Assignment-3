from django.urls import path
from . import views 

urlpatterns = [
    path('dummy/topics',views.dummyTopics),
    path('topics',views.Topics),
    path('dummy/consumer/register',views.dummyRegisterConsumer),
    path('consumer/register',views.registerConsumer),
    path('producer/register',views.registerProducer),
    path('dummy/producer/produce',views.dummyEnqueue),
    path('producer/produce',views.enqueue),
    path('dummy/consumer/consume',views.dummyDequeue),
    path('consumer/consume',views.dequeue),
    path('consumer/probe',views.probe),
    path('size',views.size),
    path('health', views.health),
]