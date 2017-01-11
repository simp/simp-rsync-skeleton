#!/usr/bin/rake -T

require 'simp/rake'

class RsyncPkg < Simp::Rake::Pkg
  def define_clamsync
    clambase = 'environments/simp/rsync/Global/clamav'

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

      Dir.chdir('environments/simp/rsync') do
        facl_files = File.read('.rsync.facl').split("\n").collect{|x| if x =~ /^#\s+file:\s+(.*)\s*$/ then x = $1 end }.compact
        present_files = []
        Find.find('.') do |path|
          Find.prune if File.symlink?(path)
          # Skip these since they're only build files/dirs.
          Find.prune if [
            './.rsync.facl',
            './build',
            './dist',
            './Rakefile',
            './README'
          ].include?(path)
          Find.prune if path =~ /.*\/\.git.*/
          Find.prune if File.basename(path) == '.shares'

          if path =~ /^\.\/(.*)/ then present_files << $1 end
        end

        file_diff = present_files - facl_files

        unless file_diff.empty?
          require 'pry'
          binding.pry
          raise(Exception,"Error: The following files do not have FACL entries:\n  #{file_diff.sort.uniq.join("\n  ")}")
        end

        # Now, check that the facl file has valid entries for the existing
        # tree.
        facl_test = %x{setfacl --test --restore=.rsync.facl 2>&1}.split("\n")

        # We have a situation where we could either get the ClamAV CVD files or
        # incremental CLD files. This is extra super fun so we have to parse the
        # data set if the check fails.
        if !$?.success?
          bad_results = []
          facl_test.each_with_index do |x,i|
            if x =~ /No such file or directory/
              bad_results << facl_test[i]
            end
          end
          facl_test.delete_if{|x| x =~ /No such file or directory/ }

          bad_results.map!{ |x| x = x.split(':')[1].strip}

          clamav_hits = []
          bad_results.each_with_index do |x,i|
            if x =~ /clamav\/.*\.c(v|l)d/
              clamav_hits << bad_results[i]
            end
          end
          bad_results.delete_if{|x| x =~ /clamav\/.*\.c(v|l)d/}

          if bad_results.empty?
            # This just returns the DB name that got missed.
            clamav_hits.each do |hit|
              next if facl_test.index{|x| x =~ /#{hit.split('.')[0..-2].join('.')}/}
              bad_results << hit
            end
          end

          unless bad_results.empty?
            raise(Exception,"Error: The following had rsync FACL errors:\n  #{bad_results.sort.uniq.join("\n  ")}")
          end
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
  t.ignore_changes_list << "#{t.pkg_name}/environments/simp/rsync/Global/clamav"
  ::CLOBBER.include("#{t.base_dir}/environments/simp/rsync/Global/clamav/*")
end
