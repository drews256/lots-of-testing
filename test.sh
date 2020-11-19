#!/bin/bash
git clone https://github.com/drews256/kegmeister.git $1/kegmeister
cd $1/kegmeister
touch diff
git diff HEAD^1 > diff
git reset --hard $1
source ~/.bashrc
asdf reshim

RV=`bundle platform --ruby`
IFS=', ' read -r -a array <<< $RV
V=${array[1]:-2.4.1}
echo $V | cut -c 1-5
RUBYVERSION=$(echo $V | cut -c 1-5)
echo $RUBYVERSION
if [ $V == 'ruby' ]
then
  asdf local ruby 2.4.1
else
  asdf local ruby ${RUBYVERSION}
fi

bundle add rubrowser
bundle add simplecov-json
bundle add minitest-reporters-json_reporter

sed -i '.bak' '1s/^/require "minitest\/reporters\/json_reporter"\
/' test/test_helper.rb
sed -i '.bak' '2s/^/Minitest::Reporters.use! [Minitest::Reporters::JsonReporter.new]\
/' test/test_helper.rb
sed -i '.bak' '3s/^/ require "simplecov-json"\
/' test/test_helper.rb
sed -i '.bak' '4s/^/SimpleCov.formatter = SimpleCov::Formatter::JSONFormatter\
/' test/test_helper.rb
bundle install
spring stop
touch test/test_results.json
bundle exec rails test > test/test_results.json
