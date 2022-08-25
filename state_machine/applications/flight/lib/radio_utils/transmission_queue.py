from . import priority_queue as pq

queue = []
limit = 100

def push(msg):
    if len(queue) < limit:
        pq.push(queue, msg)
    else:
        raise Exception("Queue is full")

def peek():
    return queue[0]

def pop():
    return pq.pop(queue)

def empty():
    return len(queue) == 0

def clear():
    global queue
    queue = []
