%global _binaries_in_noarch_packages_terminate_build 0
%global rsync_dir /var/simp/environments/simp/rsync
%global current_date %(date)

Summary: SIMP rsync repository
Name: simp-rsync
Version: 6.2.1
Release: 1%{?dist}
License: Apache License, Version 2.0 and ISC
Group: Applications/System
Source: %{name}-%{version}-%{release}.tar.gz
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires: rsync
Requires: acl
Requires: simp-environment-selinux-policy

Provides: simp_rsync_filestore = %{version}
Obsoletes: simp_rsync_filestore >= 1.0.0
Buildarch: noarch

Prefix: %{rsync_dir}

%description
Contains SIMP items that are likely to be manipulated by the user and/or too
large to transfer via Puppet.

%prep
%setup -q

%build

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

mkdir -p %{buildroot}/%{prefix}

# Install all items but ignore the build components.
tar --exclude-vcs -cf - environments | (cd %{buildroot}/var/simp && tar -xBf -)

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(0640,root,root,0750)
%doc CONTRIBUTING.md LICENSE README.md
%config %{rsync_dir}/.rsync.facl
%config(noreplace) %{rsync_dir}

%pre
#!/bin/sh
# Remove the directories that we're going to replace with symlinks.
if [ -d %{rsync_dir} ]; then
  for dir in `find %{rsync_dir} -type d -name 'linux-install'`; do
  (
    cd $dir
    rm -rf rhel{5,6,7}_i386
    rm -rf rhel{5,6,7}_x86_64
  )
  done
fi

# Make sure upgrades work properly!
if [ $1 == 2 ]; then
  if [ -d %{rsync_dir} ]; then
    for dir in `find %{rsync_dir} -type d -name 'bind_dns'`; do
    (
      cd $dir/..

      tmpdir=`ls bind_dns | grep -ve "\(your.domain\|default\)" | head -1`

      if [ -n "$tmpdir" ] && [ ! -d 'bind_dns/default' ]; then
        ln -s $tmpdir bind_dns/default
      fi
    )
    done
  fi
fi

%post
#!/bin/sh
# Post installation stuff

cd %{rsync_dir};

# Create a CentOS link if a directory or link doesn't exist
for dir in `find . -type d -name 'RedHat'`; do
  (
    cd $dir/..

    if [ ! -d "CentOS" ] && [ ! -h "CentOS" ]; then
      ln -sf RedHat CentOS;
    fi
  )
done

find . -type f -name "*.rpmnew" -delete

# Set the FACLs on the files so that we don't make a Windows box
setfacl --restore=.rsync.facl 2>/dev/null;

%preun
# Only do this on uninstall
if [ $1 -eq 0 ]; then
  # Clean up the CentOS link if present
  if [ -d %{rsync_dir} ]; then
    find %{rsync_dir} -type l -name 'CentOS' -delete
  fi
fi

%postun
# Post uninstall stuff
%changelog
* Tue May 14 2019 Jeanne Greulich <jeanne.greulich@onyxpoint.com> - 6.2.1-1
- Remove dependency on simp-environment, which will be removed in
  SIMP 6.4 and renamed to simp-environment-skeleton
- Add dependency for simp-environment-selinux-policy
  to make sure selinux policy for /var/simp directory is not
  removed.
- This module is not needed for new installs after 6.4 and is replaced
  by simp-rsync-skeleton.  This module should not
  be removed in existing systems if there is a `simp` environment because
  it will remove the files under /var/simp/environments/simp/rsync.

* Thu Apr 26 2018 Liz Nemsick <lnemsick.simp@gmail.com> - 6.2.1-0
- Added logic in dhcpd.conf to select the appropriate PXEboot file
  based on the boot type (BIOS or UEFI).

* Thu Oct 26 2017 Jeanne Greulich <jeanne.greulich@onyxpoint.com> - 6.2.0-0
- The selinux policy in simp-environment was changing settings on rsync
  files not in the simp environment.  If DNS and DHCP were running in an
  environment other then simp, relabeling the filesystem would change the
  selinux context to default context for /var/simp. This, in turn, caused
  these services to fail if selinux was in enforcing mode.
- The selinux policy and the logic to set it up were moved to simp-environment module
  so the selinux policy for /var/simp directory would be in one spot.
- Simp-rsync now requires the simp-environment

* Wed Sep 06 2017 Trevor Vaughan <tvaughan@onyxpoint.com> - 6.1.0-0
- Removed the rsync-clamav RPM from the build since it has proven to not be
  useful to most users.

* Fri Aug 18 2017 Jeanne Greulich <jeanne.greulich@onyxpint.com> - 6.0.2-0
- Added selinux context for the snmp rsync directories.

* Mon Mar 20 2017 Trevor Vaughan <tvaughan@onyxpoint.com> - 6.0.1-0
- Updated the README that is delivered with the SIMP rsync environments to talk
  a bit about the shares structure and to encourage users to read the HOWTO

* Wed Jan 11 2017 Trevor Vaughan <tvaughan@onyxpoint.com> - 6.0.0-0
- Now works with multiple environments
- Removed all legacy 'fix' code

* Wed Nov 25 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.1.0-3
- Fixed 'preun' bug that resulted in the 'CentOS' symlink being removed upon
  package upgrade.

* Fri Oct 30 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.1.0-2
- Ensure that spurious error messages are not thrown at package install time.

* Mon Jul 13 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.1.0-1
- Added a ClamAV specific RPM to handle the different license in ClamAV.
- These should eventually be split.

* Fri May 15 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.1.0-0
- Removed everything that *may* fall under a conflicting license. We will need
  to evaluate how to handle package building going forward.

* Wed Mar 11 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.0.0-4
- Removed all jenkins plugins since we were not properly maintaining them.
- Updated all TFTPBoot material to support RHEL7.1 and CentOS/RHEL6.6.

* Sun Nov 02 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.0.0-3
- Add corrected RHEL7 PXEBoot images to rsync

* Thu Aug 07 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.0.0-2
- Added the CentOS7 PXEBoot images to rsync

* Mon Jul 21 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.0.0-1
- Updated to allow for the splitting of the rsync space by facts. OS
  and major version by default.
- Also updated to use /var/simp instead of /srv for the defaults.

* Mon Jun 23 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 5.0.0-0
- Added the RHEL7 PXEBoot images to rsync.
- Removed the RHEL/CentOS5 PXEBoot images.

* Wed Apr 30 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-0
- Removed the openldap directory from rsync since it is no longer required.
- Moved the 'domains' directory to 'bind_dns' and renamed
  'your.domain' to 'default' to be more clear with new systems.
- Added a script snippet to the %pre section to move your current
  default (hopefully) to 'default' if it doesn't currently exist.
- Updated the SELinux and FACL rules appropriately.
- Updated rsync repos for the new 4.1 release
- Much of the material in global_etc is now gone

* Wed Feb 05 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.1-14
- Added the correct SELinux context to cron.daily/prelink.

* Thu Jan 02 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.1-13
- Removed the /etc/cron.daily/logrotate file from the rsync space. It
  is provided by the logrotate RPM and no additional management should
  be necessary here.

* Tue Dec 10 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.1-12
- Updated the clamav permissions to use 409 for the group instead of the clamav
  group 410. The clamav group is no longer used.

* Mon Oct 28 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.1-11
- Modified the default named.conf to deny transfers by default.
- Modified the logging statements to send regular logs to the normal
  syslog channel and security relevant logs to local6:notice.

* Thu Oct 24 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.1-10
- Fixed the permissions on the git.hpi jenkins module.

* Wed Jul 31 2013 Trevor Vaughan <tvaughan@onyxpoint.com> 4.0.1-9
- Updated the SELinux file contexts to support the case where named is
  chrooted and the system is in permissive mode. The previous release
  would continually restart named.

* Mon May 13 2013 Trevor Vaughan <tvaughan@onyxpoint.com> 4.0.1-8
- Added SELinux policies to the package to cover clamav, dhcpd,
  openldap, tftpboot, etc, named, and freeradius.
- Running 'fixfiles -R simp-rsync restore' will fix your rsync space
  if you happen to damage it.

* Thu Mar 21 2013 Maintenance
4.0.1-7
- Updated the rsync facl file to properly set permissions on the
  tftpboot directory.
- Removed old files that were no longer being rsync'd.

* Wed Mar 13 2013 Maintenance
4.0.1-6
- Added CentOS6.4 and RHEL6.4 to tftpboot.
- Removed CentOS6.2 and RHEL6.2 from tftpboot.

* Tue Feb 19 2013 Maintenance
4.0.1-5
- Updated the clamav file permissions again and nailed them down
  properly in the clamav module. It turns out that the clamav RPM does
  not specify a UID/GID.

* Mon Dec 10 2012 Maintenance
4.0.1-4
- Updated the clamav file permissions to properly match the manifests.

* Tue Nov 20 2012 Maintenance
4.0.1-3
- Updated the cron files in global_etc to change the settings such
  that they are RHEL/CentOS 6 compatible. The previous instances
  caused daily cron jobs to run twice.

* Sat Sep 22 2012 Maintenance
4.0.1-2
- A warning about TMOUT already being set will no longer print.

* Thu Jun 07 2012 Maintenance
4.0.1-1
- Added CentOS5.8 and RHEL5.8 to tftpboot.
- Removed CentOS5.7 and RHEL5.7 from tftpboot.
- Removed checkdev.cron from cron.weekly since auditd will record any
  device creation on the system and checkdev.cron was causing
  inordinate amounts of load on networked filesystems.
- Added a snippet to the %post section of the RPM to remove
  checkdev.cron from active systems that are being upgraded.

* Tue Mar 06 2012 Maintenance
4.0.1-0
- Added jenkins plugins to rsync.
- Renamed to simp-filestore for consistency.

* Tue Jan 10 2012 Maintenance
4.0-1
- Added the _binaries_in_noarch_packages_terminate_build 0 option to ensure
  that the files in the rsync repo do not incorrectly fail the build.

* Mon Dec 26 2011 Maintenance
4.0-0
- Updated the spec file to not require a separate file list.

* Fri Aug 05 2011 Maintenance
3.0-1
- Updated RHEL5 to 5.7

* Wed Jul 27 2011 Maintenance
3.0-0
- Removed i386 entries from tftpboot.
- Removed RHEL6.0 entries from tftpboot and replaced them with RHEL6.1.
- Removed miscellaneous bogus entries from the facl file.
- Updated the spec file to replace the symlink directories for both RHEL5 and
  RHEL6.
- Added 'acl' as a RPM dependency.

* Fri Jul 15 2011 Maintenance 1.0-8
- Updated the tftpboot space to support RHEL6
- Updated the spec file to remove both RHEL5 and RHEL6 to support the symlink placement.

* Wed Jun 01 2011 Maintenance 1.0-7
- Removed /srv/rsync/default/global_etc/pam.d/su due to the addition of
  pam::wheel.
- Modified the %post section of this spec file to search out and destroy that
  file on the server.

* Fri Feb 04 2011 Maintenance 2.0.0-1
- Removed 5.4 and 5.5 from tftpboot and added 5.6 and 6.0.
- Updated cron.daily/tmpwatch to be in-line with the Red Hat defaults.

* Tue Jan 11 2011 Maintenance
2.0.0-0
- Refactored for SIMP-2.0.0-alpha release

* Thu Dec 09 2010 Maintenance 1.0-5
- Fix the spec file so that the ACL is properly applied!
- The stock Apache files are no longer included since the apache module no
  longer purges.
- main.cvd has been added to the clamav directory and daily.cvd is pulled down
  at build time by the Rakefile.

* Tue Nov 09 2010 Maintenance 1.0-4
- The move to git dropped all empty directories, so we're making them in the
  spec file instead.

* Mon Oct 04 2010 Maintenance
1.0-3
- Added 'forward only;' to the '.' realm of the main DNS template.

* Wed Jul 14 2010 Maintenance
1.0-2
- Added files for freeradius
- Updated ACL file for tftpboot/rhel5.5

* Fri Jul 02 2010 Maintenance
1.0-1
- Added FreeRADIUS schema to the set of default schemas.
- Removed RHEL5.2 from tftpboot
- Added RHEL5.5 to tftpboot

* Mon May 10 2010 Maintenance
1.0-0
- Minor updates to the ACL file.

* Fri May 07 2010 Maintenance
0.2-8
- Removed the logwatch cron job from the rsync space. To remove this on a
  pre-existing system, you will need to do so manually.

* Mon Apr 26 2010 Maintenance
0.2-7
- Update to support new build scripts.
- Now ensure that the clamav permissions are owned by the clamav user and group
  to match the pupmod-clamav settings.

* Thu Feb 04 2010 Maintenance
0.2-6
- Added a %pre script to take care of some items that we will be replacing with
  symlinks.

* Thu Jan 28 2010 Maintenance
0.2-5
- Removed extraneous postfix directory.

* Fri Jan 15 2010 Maintenance
0.2-4
- Removed extra linux-install directory.

* Thu Jan 14 2010 Maintenance
0.2-3
- Restricted zone transfers in the default bind configuration file.
- This change will need to be done by hand on any existing systems. Simply add
    allow-transfer { "none"; };
  to the 'options' section of named.conf.

* Tue Dec 15 2009 Maintenance
0.2-1
- Added native support for PXE booting both RHEL5.2 and RHEL5.4 in the tftpboot
  directory.  Defaults to RHEL5.4 for backwards compatibility.

* Fri Dec 04 2009 Maintenance
0.2-0
- Removed postfix from the rsync space.
- Not forcibly removing for reference purposes.

* Fri Nov 06 2009 Maintenance
0.1-13
- Added directories to support clamav.

* Tue Oct 20 2009 Maintenance
0.1-12
- Added directories to support snmp.

* Thu Oct 1 2009 Maintenance
0.1-11
- Fixed /etc/postfix directory permissions
