<!-- vim-markdown-toc GFM -->

* [SIMP Rsync](#simp-rsync)
  * [Notes on Building](#notes-on-building)
  * [Usage](#usage)
    * [Copy the Repository to the skeleton directory](#copy-the-repository-to-the-skeleton-directory)
    * [To create a new environment](#to-create-a-new-environment)
    * [Restore the SELinux Contexts](#restore-the-selinux-contexts)

<!-- vim-markdown-toc -->

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

This RPM requires ``simp-environment-selinux-policy`` which contains the
selinux contexts for SIMP, including the context for the ``rsync`` directories.

To build the RPMs for this repository, you will need to enable the *earliest*
EL6 and EL7 repositories for your development system so that it can use an
SELinux Development stack that is guaranteed to work.

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

### Usage

To get full functionality out of the SIMP modules, particularly, the `simp`
module itself, you need to perform the following operations:

**NOTE:** If you're using the ``simp-environment-skeleton`` RPM, all of this is
done for you and is the recommended method for installing these files.

#### Copy the Repository to the skeleton directory

  1. ``mkdir -p /usr/share/simp/environments``
  2. Copy the ``rsync`` directory from this repository into ``/usr/share/simp/environments``
  3. ``cd /usr/share/simp/environments/rsync``
  4. ``setfacl --restore=.rsync.facl 2>/dev/null``

####  To create a new environment
  1. ``mkdir -p /var/simp/environments/<new-env name>``
  2.  rsync -a ``/usr/share/simp/environments/rsync`` ``/var/simp/environments/<new-env name>``
  3. ``cd /var/simp/environments/<new-env name>/rsync``
  4. ``setfacl --restore=.rsync.facl 2>/dev/null``

#### Restore the SELinux Contexts

If required, follow the instructions in the ``simp-environment-skeleton``
module to build the necessary SELinux policy, (it is done automatically if
installed from the ``simp-environment-selinux-policy`` RPM) and then run:

  1. ``/sbin/fixfiles -R simp-environment restore
