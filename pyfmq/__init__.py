import os
import hashlib
import urllib2
import base64
import json

BASE_URL = "https://fmq-dispatcher.herokuapp.com"

KEYS = None

class ResultAccessError(Exception):
    def __init__(self, url, e):
        self.url = url
        self.e
    def __str__(self):
        return repr(str(self.url)+":"+str(self.e))

class RegistrationError(Exception):
    def __init__(self, url, e):
        self.url = url
        self.e = e
    def __str__(self):
        return repr(str(self.url)+":"+str(self.e))

class MissingKeysError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "It appears you have not specified your keys using fmq.setKeys"

class Future:
    def __init__(self, key):
        self.key = key
    def get(self):
        # Create the REST request
        url = BASE_URL+"/results/"+str(self.key)
        req = urllib2.Request(url)
        try:
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError:
            raise ResultAccessError(url)
        return json.loads(resp.read())
    def __str__(self):
        return "A future for "+str(self.key)

class FMUReference:
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return "An FMU reference for "+str(self.key)

def setKeys(public, private):
    global KEYS
    KEYS = (public, private)

def register(fmu):
    # Open the file
    fp = open(fmu, "rb")
    # Read contents in
    contents = fp.read()
    fp.close()
    # Base64 encode (can I skip this?  Maybe if I skip JSON encoding)
    enc = base64.b64encode(contents)
    # Make a dictionary of the post request data
    data = {"fmu": enc}

    # Add keys to the payload
    if KEYS==None:
        raise MissingKeysError()
    try:
        (pubkey, seckey) = KEYS
        data['pubkey'] = pubkey
        data['seckey'] = seckey
    except ValueError:
        raise MissingKeysError()

    # Convert to JSON
    jsondata = json.dumps(data)
    # Create the REST request
    url = BASE_URL+"/register"
    req = urllib2.Request(url, data=jsondata)
    req.add_header('Content-Type', 'application/json')
    # Make the request
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        raise RegistrationError(url, e)
    # Get the response
    ref = resp.read()
    return FMUReference(str(ref))

def sim(fmu, sim_args={}, params={}, signals=[]):
    # Copy the kwarg data
    data = {"sim_args": sim_args, "params": params, "signals": signals}
    # Add the id of the fmu
    data['fmu'] = fmu.key

    # Add keys to the payload
    if KEYS==None:
        raise MissingKeysError()
    try:
        (pubkey, seckey) = KEYS
        data['pubkey'] = pubkey
        data['seckey'] = seckey
    except ValueError:
        raise MissingKeysError()

    # Turn it into JSON
    jsondata = json.dumps(data)
    # Create the REST request
    req = urllib2.Request(BASE_URL+"/simulate/"+str(fmu.key), data=jsondata)
    req.add_header('Content-Type', 'application/json')
    # Make the request
    resp = urllib2.urlopen(req)
    # Get the response
    ref = resp.read()
    return Future(ref)
