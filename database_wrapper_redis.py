"""
Database Wrapper for Redis
"""

import logging

import redis

def byte_to_string(byte_string):
    "convert bytes type to string"
    return byte_string.decode('utf-8')

def convert_all_byte_to_string(obj):
    "convert all bytes type in the object to string"
    if isinstance(obj, bytes):
        return byte_to_string(obj)
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(map(convert_all_byte_to_string, obj))
    if isinstance(obj, dict):
        return dict(map(convert_all_byte_to_string, obj.items()))
    return obj

class DatabaseWrapperRedis: #pylint: disable=too-few-public-methods
    "primarily for namespaces, also for automatic bytes->str conversion"
    def __init__(self, host, port, db, namespace=''):
        self.namespace = namespace
        self.database = redis.StrictRedis(host, port, db)
        self.explicitly_handled_methods = [
            'get', 'set', 'delete', 'expire',
            'lpush', 'lpop', 'rpush', 'rpop', 'llen', 'lrange',
            'sadd', 'srem', 'smembers', 'sismember',
            ]
    def __getattr__(self, attr_name):
        if attr_name in self.explicitly_handled_methods:
            def fun(key, *args, **kwargs):
                """call the function with the key properly capsuled,
                    and convert the result from bytes to str"""
                return convert_all_byte_to_string(
                    getattr(self.database, attr_name)(self.capsule(key), *args, **kwargs)
                    )
        else:
            def fun(*args, **kwargs):
                """call redis.StrictRedis object's function with its argument,
                    and convert the result from bytes to str"""
                return convert_all_byte_to_string(
                    getattr(self.database, attr_name)(*args, **kwargs)
                    )
        return fun
    def capsule(self, key):
        "capsule the key with its namespace"
        if self.namespace == '':
            return key
        capsuled_key = '%s:%s' % (self.namespace, key)
        logging.debug('capsule(%s) = %s', key, capsuled_key)
        return capsuled_key
