#!/usr/bin/rake -T

require 'simp/rake'

class RsyncPkg < Simp::Rake::Pkg
  def define_clamsync
    clambase = 'RedHat/7/clamav'

    namespace :pkg do
      desc <<-EOM
        Sync the ClamAV databases
        Update the build/freshclam.conf file to suit your environment if you want to
        download from anywhere besides the official ClamAV mirrors.
      EOM
      task :clamsync do
        mkdir(clambase) unless File.exist?(clambase)

        verbose(true) { sh %{freshclam --config-file=build/freshclam.conf} }
        rm("#{clambase}/mirrors.dat") if File.exist?("#{clambase}/mirrors.dat")
      end
    end
  end

  def define_check_facl
    desc "Check the .rsync.facl file for unknown files"
    task :check_facl do
      # First, check to make sure that we actually have a facl entry for
      # everything in our tree.

      facl_files = File.read('.rsync.facl').split("\n").collect{|x| x =~ /^#\s+file:\s+(.*)\s*$/ and x = $1}.compact
      present_files = []
      Find.find('.') do |path|
        Find.prune if File.symlink?(path)
        # Skip these since they're only build files/dirs.
        Find.prune if [
          './.rsync.facl',
          './build',
          './dist',
          './Rakefile'
        ].include?(path)
        Find.prune if path =~ /.*\/\.git.*/

        path =~ /^\.\/(.*)/ and path = $1

        present_files << path
      end

      file_diff = present_files - facl_files

      if not file_diff.empty? then
        raise(Exception,"Error: The following files do not have FACL entries:\n  #{file_diff.sort.uniq.join("\n  ")}")
      end

      # Now, check that the facl file has valid entries for the existing
      # tree.
      facl_test = %x{setfacl --test --restore=.rsync.facl 2>&1}.split("\n")

      # We have a situation where we could either get the ClamAV CVD files or
      # incremental CLD files. This is extra super fun so we have to parse the
      # data set if the check fails.
      if !$?.success? then
        bad_results = []
        facl_test.each_with_index do |x,i|
          if x =~ /No such file or directory/ then
            bad_results << facl_test[i]
          end
        end
        facl_test.delete_if{|x| x =~ /No such file or directory/ }

        bad_results.map!{ |x| x = x.split(':')[1].strip}

        clamav_hits = []
        bad_results.each_with_index do |x,i|
          if x =~ /clamav\/.*\.c(v|l)d/ then
            clamav_hits << bad_results[i]
          end
        end
        bad_results.delete_if{|x| x =~ /clamav\/.*\.c(v|l)d/}

        if bad_results.empty? then
          # This just returns the DB name that got missed.
          clamav_hits.each do |hit|
            next if facl_test.index{|x| x =~ /#{hit.split('.')[0..-2].join('.')}/}
            bad_results << hit
          end
        end

        if not bad_results.empty? then
          raise(Exception,"Error: The following had rsync FACL errors:\n  #{bad_results.sort.uniq.join("\n  ")}")
        end
      end
    end
  end

  def define
    define_clamsync
    define_check_facl
    super
    # Add on the needed prereqs
    Rake::Task['pkg:tar'].enhance([:clamsync, :check_facl])
  end
end

RsyncPkg.new(File.dirname(__FILE__)) do |t|
  t.ignore_changes_list << "#{t.pkg_name}/clamav"
  ::CLOBBER.include("#{t.base_dir}/clamav/*")
end
