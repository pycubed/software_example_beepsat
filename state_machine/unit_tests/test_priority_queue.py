import unittest
import sys

sys.path.insert(0, 'state_machine/applications/flight/lib')

import priority_queue as pq  # noqa: E402

# https://www.geeksforgeeks.org/how-to-check-if-a-given-array-represents-a-binary-heap/
def _isHeap(arr, i, n):

    # If (2 * i) + 1 >= n, then leaf node, so return true
    if i >= int((n - 1) / 2):
        return True

    # If an internal node and is greater
    # than its children, and same is
    # recursively true for the children
    if(arr[i] >= arr[2 * i + 1] and
       arr[i] >= arr[2 * i + 2] and
       _isHeap(arr, 2 * i + 1, n) and
       _isHeap(arr, 2 * i + 2, n)):
        return True

    return False

def isHeap(arr):
    return _isHeap(arr, 0, len(arr))

class Heapify(unittest.TestCase):

    def test(self):
        h1 = [3, 8, 17, 4]
        self.assertTrue(isHeap(pq.heapify(h1)))
