""" Implements protocol for talking to local Coq installation.
"""

import subprocess, shlex
import time
# The solutions here are *Nix-specific.
import fcntl, os
from Popen_noblock import Popen_async, Empty

def getline(q):
  ret = ''
  cur = ''
  while cur != '\n':
    cur = q.get(True)
    ret += cur
  return ret

def getall(q, timeout=0.1):
  ret = ''
  while True:
    try:
      ret += q.get(timeout=timeout)
    except Empty:
      return ret

class Coq_Local(object):
  def __init__(self, coqtop = "/usr/bin/coqtop"):
    """ Open a Coq process.
      - coqtop: Location of coqtop executable.
      - timeout: How long to wait for coqtop to print to stdout.
    """
    self._coqtop = Popen_async(shlex.split(coqtop) + ["-emacs"],
                               stdin  = subprocess.PIPE,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE)

    # Clear Coq greeting.
    data = self._read_coq()
    if not data:
      print "Could not manage coq."

  def _read_coq(self):
    """ Read data from Coqtop. Read stdout after the  """
    error = getline(self._coqtop.stderr)

    return self._clean(getall(self._coqtop.stdout, timeout=0.1))

  def _clean(self, string):
    """ Clean a string. """
    return "".join([c for c in string if ord(c) != 253])

#  def __del__(self):
#    """ Clean up: stop Coq process. """
#    self._coqtop.terminate()

  def send(self, command):
    """ Send data to Coqtop, returning the result. """
    self._coqtop.stdin.write(command + "\n")
    self._coqtop.stdin.flush()

    return self._read_coq()
