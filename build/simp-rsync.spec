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
Version: 7.1.0
Release: 1
License: Apache License, Version 2.0 and ISC
Group: Applications/System
Source: %{name}-%{version}-%{release}.tar.gz
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires: rsync
Requires: simp-environment-skeleton >= 7.0.0
Requires: simp-selinux-policy
Requires: acl

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

%post
#!/bin/sh
# Post installation stuff

%preun

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
