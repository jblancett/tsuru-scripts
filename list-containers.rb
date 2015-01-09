#!/usr/bin/env ruby

require 'mongo'
require 'highline/import'
require 'optparse'

mongo = Mongo::MongoClient.new
ui = HighLine.new

container_list = [
  ui.color('Address', :bold),
  ui.color('Name', :bold),
  ui.color('App', :bold),
  ui.color('Platform', :bold),
  ui.color('Status', :bold)
]

columns = container_list.length

filters = {}
OptionParser.new do |opts|

  opts.on('-a', '--app APP', 'Filter by app') do |app|
    filters['appname'] = app
  end

  opts.on('-H', '--host HOSTNAME', 'Filter by host') do |host|
    filters['hostaddr'] = host
  end

  opts.on('-p', '--platform PLATFORM', 'Filter by platform') do |platform|
    filters['type'] = platform
  end

end.parse!

mongo.db('tsuru').collection('docker_containers').find(filters).sort_by{ |container| container['hostaddr'] }.each do |container|
  container_list << "#{container['hostaddr']}:#{container['hostport']}"
  container_list << container['name']
  container_list << container['appname']
  container_list << container['type']
  container_list << container['status']
end

puts ui.list(container_list, :uneven_columns_across, columns)
