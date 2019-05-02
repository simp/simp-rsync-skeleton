%{lua:

--
-- When you build you must pass this along so that we know how to get the
-- preliminary information.
-- This directory should hold the following items:
--   * 'build' directory
--   * 'CHANGELOG' <- The RPM formatted Changelog
--

src_dir = rpm.expand('%{pup_module_info_dir}')

if string.match(src_dir, '^%%') or (posix.stat(src_dir, 'type') ~= 'directory') then
  src_dir = rpm.expand('%{_sourcedir}')

  if (posix.stat((src_dir .. "/CHANGELOG"), 'type') ~= 'regular') then
    src_dir = './'
  end
end
}

%global _binaries_in_noarch_packages_terminate_build 0
%global current_date %(date)

Summary: SIMP rsync skeleton
Name: simp-rsync-skeleton
Version: 7.0.0
Release: 0%{?dist}
License: Apache License, Version 2.0 and ISC
Group: Applications/System
Source: %{name}-%{version}-%{release}.tar.gz
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires: rsync
Requires: simp-environment-skeleton >= 7.0.0
Requires: simp-environment-selinux-policy >= 1.0.0
Requires: acl

Provides: simp_rsync_filestore = %{version}
Obsoletes: simp_rsync_filestore >= 1.0.0
Buildarch: noarch

Prefix: /usr/share/simp/environment-skeleton

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
tar --exclude-vcs -cf - rsync | (cd %{buildroot}/%{prefix} && tar -xBf -)

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(0640,root,root,0750)
%doc CONTRIBUTING.md LICENSE README.md
%config %{prefix}/rsync/.rsync.facl
%config %attr(0750,root,root) %{prefix}/rsync

%pre
#!/bin/sh
# Remove the directories that we're going to replace with symlinks.
if [ -d %{prefix}/rsync ]; then
  for dir in `find %{prefix}/rsync -type d -name 'linux-install'`; do
  (
    cd $dir
    rm -rf rhel{5,6,7}_i386
    rm -rf rhel{5,6,7}_x86_64
  )
  done
fi

# Make sure upgrades work properly!
if [ $1 == 2 ]; then
  if [ -d %{prefix}/rsync ]; then
    for dir in `find %{prefix}/rsync -type d -name 'bind_dns'`; do
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

cd %{prefix}/rsync;

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
  if [ -d %{prefix}/rsync ]; then
    find %{prefix}/rsync -type l -name 'CentOS' -delete
  fi
fi

%postun
# Post uninstall stuff
%changelog
%{lua:
-- Finally, the CHANGELOG

changelog = io.open(src_dir .. "/CHANGELOG","r")
line = changelog:read()
if string.match(line, "^*%s+%a%a%a%s+%a%a%a%s+%d%d?%s+%d%d%d%d%s+.+") then
  changelog:seek("set",0)
  print(changelog:read("*all"))
end

}
