#!/bin/bash
if [ -d "$1" ]; then
  echo "$1 is a directory."
  exit
fi

git clone https://github.com/drews256/kegmeister.git $1/kegmeister
cd $1/kegmeister
touch diff
git reset --hard $1

touch .gitattributes

sed -i '.bak' '1s/^/*.rb diff=ruby\
/' .gitattributes
sed -i '.bak' '2s/^/*.rake diff=ruby\
/' .gitattributes

git diff HEAD^1 > diff

source /usr/local/share/chruby/chruby.sh
chruby ruby-2.4.1
spring stop

gem install bundler

RV=`bin/bundle platform --ruby`
IFS=', ' read -r -a array <<< $RV
V=${array[1]:-2.4.1}
echo $V | cut -c 1-5
RUBYVERSION=$(echo $V | cut -c 1-5)
echo $RUBYVERSION
if [ $V == 'ruby' ]
then
  chruby ruby-2.4.1
else
  chruby ruby-${RUBYVERSION}
fi

bin/bundle add rubrowser
bin/bundle add simplecov-json
bin/bundle add minitest-reporters-json_reporter

echo 'here'
sed -i '.bak' '1s/^/require "minitest\/reporters\/json_reporter"\
/' test/test_helper.rb
sed -i '.bak' '2s/^/Minitest::Reporters.use! [Minitest::Reporters::JsonReporter.new]\
/' test/test_helper.rb
sed -i '.bak' '3s/^/ require "simplecov-json"\
/' test/test_helper.rb
sed -i '.bak' '4s/^/SimpleCov.formatter = SimpleCov::Formatter::JSONFormatter\
/' test/test_helper.rb

echo 'here 2'
RAILS_ENV=test rails db:create

bin/bundle install
touch test/test_results.json
rails test > test/test_results.json
