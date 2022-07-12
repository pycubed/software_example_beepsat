import lib.priority_queue as pq

queue = []

def push(msg):
    pq.push(queue, msg)

def peek():
    return queue[0]

def pop():
    return pq.pop(queue)

def empty():
    return len(queue) == 0
