#!/usr/bin/env python

import os
import sys
import json
import re
import httplib

class DockerNodeUnitList(object):
    def __init__(self):
        if 'TSURU_TOKEN' not in os.environ:
            print "missing TSURU_TOKEN"
            sys.exit(1)
        if 'TSURU_TARGET' not in os.environ:
            print "missing TSURU_TARGET"
            sys.exit(1)
        self.token = os.environ['TSURU_TOKEN']
        self.target = os.environ['TSURU_TARGET']

    def request(self, path='/apps', method='GET', data=''):
        headers = {
            'Authorization': "bearer {}".format(self.token),
            'Content-Type': 'application/json'
        }
        if self.target.startswith('https://'):
            connection = httplib.HTTPSConnection(self.target.lstrip('https://'))
        else:
            connection = httplib.HTTPConnection(self.target.lstrip('http://'))
        connection.request(method, path, data, headers)
        response = connection.getresponse()
        data = response.read()
        if data == None or data == '':
            data = '{}'
        return {
            'status': response.status,
            'data': json.loads(data)
        }


    def get_nodes(self, filters={}):
        response = self.request('/docker/node')
        if response['status'] != 200:
            print "Error fetching nodes! {}".format(response['data'])
            sys.exit(1)
        if len(filters) == 0:
            return response['data']['nodes']
        else:
            nodes = []
            for node in response['data']['nodes']:
                valid = True
                for k, v in filters.iteritems():
                    if k not in node['Metadata'] or node['Metadata'][k] != v:
                        valid = False
                if valid:
                    nodes.append(node)
            return nodes

    def get_containers(self, node):
        address = node['Address']
        protocol = re.compile('^https?://')
        address = protocol.sub('', address)
        port = re.compile(':\d+$')
        address = port.sub('', address)
        response = self.request('/docker/node/{}/containers'.format(address))
        if response['data'] == None:
            response['data'] = []
        if response['status'] != 200:
            print "Error fetching containers for node {}! {}".format(node, response['data'])
            exit(1)
        return response['data']

def usage():
    print "Usage: tsuru-admin docker-node-unit-list [--filter/-f <metadata>=<value>]"
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) > 1 and (sys.argv[1] not in ['-f', '--filter'] or len(sys.argv) == 2):
        usage()

    filters = {}
    for arg in sys.argv[2:]:
        try:
            key, value = arg.split('=',2)
        except:
            usage()
        filters[key] = value

    tsuru = DockerNodeUnitList()
    nodes = tsuru.get_nodes(filters)
    for node in nodes:
        if 'pool' in node['Metadata']:
            print '\n{}  {}'.format(node['Address'], node['Metadata']['pool'])
        else:
            print '\n{}'.format(node['Address'])
        for container in tsuru.get_containers(node):
            print "{} {} {} {}".format(container['Name'], container['AppName'], container['Type'], container['Status'])
