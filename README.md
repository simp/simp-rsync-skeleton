## SIMP Rsync

This is the default data store for the SIMP Rsync content.

By default, this is used by the ``simp`` Puppet module to ensure that various
subsystems have content that can be successfully delivered to clients.

Multiple environments are supported as well as any number of Operating Systems.
Additionally, you may freely add to the directory structure so long as there is
some reasonable way of serving the material via ``rsync``.

Any top level directory without an associated ``rsync::server::section``
resource will not be served to clients.

When updating this repository, you **must** ensure that you update the
``.rsync.facl`` file appropriately!

### Notes on Building

To build the RPMs for this repository, you will need to enable the *earliest*
EL6 and EL7 repositories for Mock so that it can use an SELinux Development
stack that is guaranteed to work.

If you are using the SIMP global build system, you should not need to make any
changes to your environment.

* EL7

```
[legacy]
name=Legacy
baseurl=http://vault.centos.org/7.0.1406/os/x86_64
gpgkey=file:///usr/share/distribution-gpg-keys/centos/RPM-GPG-KEY-CentOS-7
gpgcheck=1
```

* EL6

```
[legacy]
name=Legacy
enabled=1
baseurl=http://vault.centos.org/6.0/os/x86_64
gpgkey=file:///usr/share/distribution-gpg-keys/centos/RPM-GPG-KEY-CentOS-6
gpgcheck=1
```
