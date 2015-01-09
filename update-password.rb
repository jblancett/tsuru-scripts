#!/usr/bin/env ruby

require 'mongo'
require 'bcrypt'
require 'highline/import'

if ARGV.count != 1 && ARGV[0] != '--help'
  puts 'Usage:  ./update-password.rb USERNAME'
  exit 0
end

user = ARGV[0]

pass = ask("Enter new password for #{user}: ") do |q| 
  q.echo = false
  q.validate = Proc.new{ |a| a.length >= 6 && a.length <= 50 }
  q.responses[:not_valid] = "Password must be at least 6 characters and no more than 50"
end

mongo = Mongo::MongoClient.new
mongo.db('tsuru').collection('users').update({'email' => user},{'$set' => {'password' => BCrypt::Password.create(pass)}})
