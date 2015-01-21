#!/usr/bin/env ruby

require 'mongo'

mongo = Mongo::MongoClient.new

if ARGV.count < 2
  puts 'Usage: ./update-machine-template.rb TEMPLATE PARAM=VALUE [PARAM=VALUE]..'
  exit 0
end

collection = mongo.db('tsuru').collection('iaas_machines_templates')

template_name = ARGV.shift
template = collection.find_one({"_id" => template_name})
unless template && template["data"]
  puts "Could not find machine template named #{template}"
  exit 0
end

params = {}
template["data"].each{ |p| params[p['name']] = p['value'] }
puts "Old #{template_name} template: #{params.inspect}"
ARGV.each do |p|
  k, v = p.split('=')
  params[k] = v
end
puts "New #{template_name} template: #{params.inspect}"
data = []
params.each do |k, v|
  data << { "name" => k, "value" => v }
end

collection.update({"_id" => template_name}, {"$set" => {"data" => data}})
