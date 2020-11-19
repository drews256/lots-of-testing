require 'rubrowser'
require 'rake'

require 'rake/testtask'

Rake::TestTask.new do |t|
  t.libs.push 'test'
  t.pattern = 'test/**/*_test.rb'
  t.warning = false
  t.verbose = false
end

task :default do
  :test
end

Rake::Task['test'].execute
