from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .queue_funcs import *

import subprocess
import os
import time
import socket
import struct
import ast

# run the raft server as a different process
# 
# 
# 

# Design decision: The raft server will be run as a different process
# Design decision: The raft server will be run on a different port than the broker
# The port number of the raft server will be 9000


def dummyTopics(request):
    final_resp = {'status':'failure'}
    if request.method == 'GET':
        final_resp = listTopics()
        return JsonResponse(final_resp)

    elif request.method == 'POST':
        # create the message dictinary
        message = {'topic_name':request.POST.get('topic_name'), 'partition_no':int(request.POST.get('partition_no')), 'port':int(request.POST.get('port')), 'peers':request.POST.get('peers')}
        message = str(message)
        message = str(3) + message
        # get the broker port and raft port
        broker_port = os.environ.get('PORT')
        raft_port = 9000
        
        message_bytes = struct.pack('>i', broker_port) + message.encode('utf-8')
        # send the message to the raft server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', raft_port))
        sock.sendall(message_bytes)
        sock.close()
        # Topics(request)

def Topics(request):
    # if request.method == 'GET':
    #     final_resp = listTopics()
    #     print(final_resp)
    #     return JsonResponse(final_resp)

    if request.method == 'POST':
        final_resp = {'status':'message'}
        if request.POST.get('topic_name') == None:
            final_resp['status'] = "failure"
            final_resp['message'] = "No key 'topic_name' found in the POST method"
            return JsonResponse(final_resp)
        else:
            print("Creating the topic")
            final_resp = createTopic(request.POST.get('topic_name'), int(request.POST.get('partition_no')))
            return JsonResponse(final_resp)

def dummyRegisterConsumer(request):
    # create the message dictionary
    message = {'topic_name':request.POST.get('topic_name'), 'consumer_id':int(request.POST.get('consumer_id')), 'partition_id':int(request.POST.get('partition_id'))}
    message = str(message)
    message = str(2) + message
    # get the broker port and raft port
    broker_port = os.environ.get('PORT')
    raft_port = 9000
    message_bytes = struct.pack('>i', broker_port) + message.encode('utf-8')
    # send the message to the raft server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', raft_port))
    sock.sendall(message_bytes)
    sock.close()
    # registerConsumer(request)

def registerConsumer(request):
    final_resp = {'status':'failure'}
    if request.method == 'POST':
        # print("Hey")
        # Check if valid parameters
        if request.POST.get('topic_name') == None:
            final_resp['message'] = "No key 'topic_name' found in the POST method"
            return JsonResponse(final_resp)
        #register the consumer
        final_resp = qregisterConsumer(request.POST.get('topic_name'), request.POST.get('consumer_id'))
        return JsonResponse(final_resp)

    final_resp['status'] = 'failure'
    final_resp['message'] = 'GET method not supported for this endpoint'
    return JsonResponse(final_resp)


def registerProducer(request):
    final_resp = {'status':'failure'}
    if request.method == 'POST':
        # Check if valid parameters
        if request.POST.get('topic_name') == None:
            final_resp['message'] = "No key 'topic_name' found in the POST method"
            return JsonResponse(final_resp)
        #register the producer
        final_resp = qregisterProducer(request.POST.get('topic_name'))
        return JsonResponse(final_resp)

    final_resp['message'] = 'GET method not supported for this endpoint'
    return JsonResponse(final_resp)

def dummyEnqueue(request):
    # create the message dictinary
    message = {'topic_name':request.POST.get('topic_name'), 'message':request.POST.get('message'), 'partition_no':int(request.POST.get('partition_no'))}
    message = str(message)
    message = str(0) + message
    # get the broker port and raft port
    broker_port = os.environ.get('PORT')
    raft_port = 9000
    message_bytes = struct.pack('>i', broker_port) + message.encode('utf-8')
    # send the message to the raft server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', raft_port))
    sock.sendall(message_bytes)
    sock.close()
    # enqueue(request)

def enqueue(request):
    final_resp = {'status':'failure'}
    if request.method == 'POST':
        # Check if valid parameters
        if request.POST.get('message',None) == None:
            final_resp["message"] = "No key 'message' found in the POST method"
            return JsonResponse(final_resp)
        if request.POST.get('topic_name') == None:
            final_resp["message"] = "No key 'topic_name' found in the POST method"
            return JsonResponse(final_resp)
        # if request.POST.get('producer_id') == None:
        #     final_resp["message"] = "No key 'producer_id' found in the POST method"
            return JsonResponse(final_resp)
        if request.POST.get('partition_no') == None:
            final_resp["message"] = "No 'partition_no' found in the GET method"
            return JsonResponse(final_resp)

        #Add the log message to the queue
        final_resp = qenqueue(request.POST.get('topic_name'),request.POST.get('message'),request.POST.get('partition_no'))
        return JsonResponse(final_resp)

    final_resp['message'] = 'GET method not supported for this endpoint'
    return JsonResponse(final_resp)

def dummyDequeue(request):
    # create the message dictinary
    message = {'topic_name':request.GET.get('topic_name'), 'consumer_id':int(request.GET.get('consumer_id')), 'partition_no':int(request.GET.get('partition_no'))}
    message = str(message)
    message = str(1) + message
    # get the broker port and raft port
    broker_port = os.environ.get('PORT')
    raft_port = 9000
    message_bytes = struct.pack('>i', broker_port) + message.encode('utf-8')
    # send the message to the raft server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', raft_port))
    sock.sendall(message_bytes)
    sock.close()
    # dequeue(request)

def dequeue(request):
    final_resp = {'status':'failure'}
    if request.method == 'GET':
        # Check if valid parameters
        if request.GET.get('topic_name') == None:
            final_resp["message"] = "No key 'topic_name' found in the GET method"
            return JsonResponse(final_resp)
        if request.GET.get('consumer_id') == None:
            final_resp["message"] = "No key 'consumer_id' found in the GET method"
            return JsonResponse(final_resp)
        if request.GET.get('partition_no') == None:
            final_resp["message"] = "No 'partition_no' found in the GET method"
            return JsonResponse(final_resp)
        #Remove and return the log message from the queue
        final_resp = qdequeue(request.GET.get('topic_name'),request.GET.get('consumer_id'),request.GET.get('partition_no'))
        return JsonResponse(final_resp)

    final_resp['message'] = 'POST method not supported for this endpoint'
    return JsonResponse(final_resp)

def size(request):
    final_resp = {'status':'failure'}
    if request.method == 'GET':
        # Check if valid parameters
        print("YO")
        if request.GET.get('topic_name') == None:
            final_resp["message"] = "No key 'topic_name' found in the GET method"
            return JsonResponse(final_resp)
        if request.GET.get('consumer_id') == None:
            final_resp["message"] = "No key 'consumer_id' found in the GET method"
            return JsonResponse(final_resp)
        final_resp = qsize(request.GET.get('topic_name'),request.GET.get('consumer_id'), request.GET.get('partition_no'))
        return JsonResponse(final_resp)

    final_resp['message'] = 'POST method not supported for this endpoint'
    return JsonResponse(final_resp)

def probe(request):
    final_resp = {'status':'failure'}
    if request.method == 'GET':
        # Check if valid parameters
        if request.GET.get('topic_name') == None:
            final_resp["message"] = "No key 'topic_name' found in the GET method"
            return JsonResponse(final_resp)
        if request.GET.get('consumer_id') == None:
            final_resp["message"] = "No key 'consumer_id' found in the GET method"
            return JsonResponse(final_resp)
        if request.GET.get('partition_no') == None:
            final_resp["message"] = "No 'partition_no' found in the GET method"
            return JsonResponse(final_resp)

        #Return the probed message value for the specific partition for the consumer 
        final_resp = qprobe(request.GET.get('topic_name'),request.GET.get('consumer_id'),request.GET.get('partition_no'))
        return JsonResponse(final_resp)

    final_resp['message'] = 'POST method not supported for this endpoint'
    return JsonResponse(final_resp)

def health(request):
    final_resp = {'status':'alive'}
    return JsonResponse(final_resp)

def get_data(request):
    final_resp = {'status':'failure'}
    if request.method == 'GET':
        final_resp = qget_data()
        return JsonResponse(final_resp)