#!/usr/bin/env python

import pymongo, redis, os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
MONGO_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGODB_PORT', 27017)

mongo = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
redis = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

# clear cnames and frontends
for key in redis.keys('frontend:*') + redis.keys('cname:*'):
  redis.delete(key)

for app in mongo.tsuru.apps.find():
  backends = [app['name']]
  for container in mongo.tsuru.docker_containers.find({'appname': app['name']}):
    if container['appname'] == app['name']:
      backends.append("http://%s:%s" % (container['hostaddr'], container['hostport']))
  print "frontend:%s" % app['ip']
  for backend in backends:
    print "  %s" % backend
    redis.rpush("frontend:%s" % app['ip'], backend)
  if ('cname' in app and type(app['cname']) is list and len(app['cname']) > 0):
    for cname in app['cname']:
      print "frontend:%s" % cname
      for backend in backends:
        print "  %s" % backend
        redis.rpush("frontend:%s" % cname, backend)
    print "cname:%s" % app['name']
    for cname in app['cname']:
      print "  %s" % cname
      redis.rpush("cname:%s" % app['name'], cname)

