# Gemfile for bundler (gem install bundler)
#
# To update all gem dependencies:
#
#   bundle
#
# To run a rake task:
#
#   bundle exec rake <task>
# Variables:
#
# SIMP_GEM_SERVERS | a space/comma delimited list of rubygem servers
# PUPPET_VERSION   | specifies the version of the puppet gem to load
# ------------------------------------------------------------------------------
gem_sources   = ENV.key?('SIMP_GEM_SERVERS') ? ENV['SIMP_GEM_SERVERS'].split(/[, ]+/) : ['https://rubygems.org']

gem_sources.each { |gem_source| source gem_source }

# mandatory gems
gem 'bundler'
gem 'rake'
gem 'simp-rake-helpers', ENV.fetch('SIMP_RAKE_HELPERS_VERSION', ['>= 5.2', '< 6.0'])

# although we have no tests, these are pulled in by simp-rake-helpers
# so need to make sure have correct simp-beaker-helpers to deal
# with Ruby 2.1.9 gem issues
group :system_tests do
  gem 'beaker'
  gem 'beaker-rspec'
  gem 'simp-beaker-helpers', ENV.fetch('SIMP_BEAKER_HELPERS_VERSION', ['>= 1.10.8', '< 2.0'])
end

