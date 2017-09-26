# ansible-role-dpb

Creates `chroot` for bulk package build and configures `dpb` build environment.

At the initial play, the ports tree is updated to the latest in a tag. It is
user's responsibility to update the tree afterwards. A handler is provided to
update the ports tree in host and sync files in `chroot`.

`cvs(1)` is used in the role to retrieve and update the ports tree. However, it
is subject to change in the future, and other version management might be used.

# Requirements

None

# Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `dpb_build_user` | build user | `_pbuild` |
| `dpb_build_group` | build group | `{{ dpb_build_user }}` |
| `dpb_fetch_user` | fetch user | `_pfetch` |
| `dpb_fetch_group` | fetch group | `{{ dpb_fetch_user }}` |
| `dpb_conf_dir` | path to directory to keep configuration files | `/etc/dpb` |
| `dpb_conf_file` | files that contains a list of packages to build | `{{ dpb_conf_dir }}/packages` |
| `dpb_cache_directory` | path to cache directory where sets and ports file are kept | `/var/cache/dpb` |
| `dpb_sets` | list of necessary sets | `["comp", "xbase", "xfont", "xshare"]` |
| `dpb_ftp_mirror_url_base` | string of `scheme://` + `hostname` | `http://ftp.openbsd.org` |
| `dpb_ftp_mirror_url_path` | path to the mirror root directory | `/pub/OpenBSD` |
| `dpb_signify_key_dir` | path to directory where public keys are kept | `/etc/signify` |
| `dpb_cvsroot` | mandatory `CVSROOT` string | `""` |
| `dpb_cvs_tag` | optional CVS tag. when empty, appropriate default will be set (`OPENBSD_6_0` if the release version is 6.0) | `""` |
| `dpb_proot_conf_file` | path to configuration file of `proot` | `{{ dpb_conf_dir }}/proot.conf` |
| `dpb_proot_chroot` | mandatory path to `chroot(2)` directory | `""` |
| `dpb_proot_config` | dict of `proot` configuration | see below |
| `dpb_remove_nodev_mount_option` | if `true` value is set and the mount point of `dpb_proot_chroot` is mounted with `nodev`, remove `nodev` mount option | `no` |

## `dpb_proot_config`

This is a dict for `proot`. Each key is described in
[`proot(1)`](http://man.openbsd.org/proot) man page.

Values are string except `actions` and `mkconf_lines`.

`actions` is a list of actions.

`mkconf_lines` is a list of lines to be added to `mk.conf` in `chroot`.

```yaml
dpb_proot_config:
  chroot: "{{ dpb_proot_chroot }}"
  BUILD_USER: "{{ dpb_build_user }}"
  FETCH_USER: "{{ dpb_fetch_user }}"
  chown_all: 1
  actions:
    - unpopulate_light
    - resolve
    - copy_ports
  mkconf_tail: /dev/null
```

Do not omit `mkconf_tail` when `mkconf_lines` is set. `proot` has a bug and
`mk.conf` will not be created under certain conditions. See comments in Example
Playbook. Set the variable to `/dev/null` even when you do not use it just in
case.

## `dpb_proot_chroot` and `dpb_remove_nodev_mount_option`

It is generally, and strongly, recommended to provide a dedicated partition for
`dpb_proot_chroot` without `nodev` option and to set
`dpb_remove_nodev_mount_option` to `no`, which is the default (the chroot needs
device nodes).

When `dpb_remove_nodev_mount_option` is set to `yes` and the mount point of
`dpb_proot_chroot` is mounted with `nodev`, the partition will be re-mounted
without `nodev` and `fstab(5)` will be modified. This affects all the
sub-directories of the mount point.

# Dependencies

None

# Example Playbook

```yaml
- hosts: localhost
  roles:
    - reallyenglish.ssh
    - ansible-role-dpb
  vars:
    ssh_known_hosts:
      - name: anoncvs.ca.openbsd.org
        state: present
        key: "anoncvs.ca.openbsd.org ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCz6RLtgGksBp/0dH7M5vGCUxgD31+wX28tnLlij90+cYhjELDV3HX95DypEA7xfIN6W8Vg/GOJkX4Oot+zpQXNQx3VeOyMgcn4KXO83XYGsPVfJQijjzyI0r0/ztEsxYAE6JHEiEvY9floDnNRyoFLVETNE5oB9yBcDIt6W6BYjlpXqJNsEPy7ij+kBbEk7QT0FcyFidp7FmExsOQy23nhQ55A/6fB7ATsDQtz+snniF9ZJg5+b71SYzxfhUPkxJhmhBkx7NmPnRjy7eE0I7qrHODrHONIi1LWCo0joTIAfVgxhEn5SDbviTAINAecGgis5LQqXp0xSupfWuozZeXV"
    dpb_proot_chroot: /usr/local/build
    dpb_cvsroot: anoncvs@anoncvs.ca.openbsd.org:/cvs
    dpb_packages:
      - net/rsync
      - sysutils/ansible
      - net/curl
    dpb_proot_config:
      chroot: "{{ dpb_proot_chroot }}"
      BUILD_USER: "{{ dpb_build_user }}"
      FETCH_USER: "{{ dpb_fetch_user }}"
      chown_all: 1
      actions:
        - unpopulate_light
        - resolve
        - copy_ports
      # XXX when `mkconf_lines` contains something, `proot` should create
      # `mk.conf`, but it does not. it does when:
      #
      # * "some directory values are different from the default"
      # * or `mkconf_tail` is not empty
      #
      # set `mkconf_tail` here to ensure `mk.conf` is always created. if one of
      # attributes related to `mk.conf`, such as `PORTSDIR`, is different from
      # the defaults, `mkconf_tail` can be removed.
      mkconf_tail: /dev/null
      mkconf_lines:
        - FETCH_CMD = /usr/bin/ftp -E
        - FETCH_CMD = /usr/bin/ftp -E
    # XXX this is not recommended but the box does not have additional
    # partition.
    dpb_remove_nodev_mount_option: yes
```

# License

```
Copyright (c) 2017 Tomoyuki Sakurai <tomoyukis@reallyenglish.com>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

# Author Information

Tomoyuki Sakurai <tomoyukis@reallyenglish.com>

This README was created by [qansible](https://github.com/trombik/qansible)
