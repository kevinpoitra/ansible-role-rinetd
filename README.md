Ansible `rinetd` Role
=========

Installs and generates configuration for [rinetd](https://github.com/samhocevar/rinetd), a network traffic redirector.

Role Variables
--------------

### `rinetd_install_source`
#### *(required, defaults to `github_releases`)*

The source of which `rinetd` should be acquired from. There are two possible options:

- `repo` - Installs `rinetd` from the system's package repository, `apt`.
- `github_releases` - Installs `rinetd` from [the recommended fork from samhocevar](https://github.com/samhocevar/rinetd) via the GitHub Releases system.

Defaults to `github_releases`. This is done as the version of `rinetd` within apt repositories is outdated and does not support newer `rinetd` features such as UDP redirection, as is the case with Debian Bullseye.

---

### `rinetd_allowed_hosts`
#### *(optional)*

A list of allowed hosts. Each group of hosts can optionally be denoted by a comment that'll be included in the generated `rinetd` configuration. The groupings themselves don't matter to `rinetd`,

This allows you to define groups of hosts that are optionally denoted by a comment.

Example:
```yaml
rinetd_allowed_hosts:
  - comment: 'Allowed LAN group 1'
    hosts:
      - 192.168.2.*
      - 192.168.3.4
  - hosts:
      - fe80:*
```

Generated configuration:

```
# Allowed LAN group 1
allow 192.168.2.*
allow 192.168.3.4

allow fe80:*
```

---

### `rinetd_denied_hosts`
#### *(optional)*

A list of denied hosts.

This works similarly to `rinetd_allowed_hosts`, but denies hosts instead.

Example:

```yaml
rinetd_denied_hosts:
  - comment: 'Denied IPv4 hosts'
    hosts:
      - 192.168.2.1?
  - comment: 'Denied IPv6 hosts'
    hosts:
      - 2001:618:*:e43f
```

Generated configuration:

```
# Denied IPv4 hosts
deny 192.168.2.1?

# Denied IPv6 hosts
deny 2001:618:*:e43f
```

---

### `rinetd_default_ipv4_bindaddress`
#### *(optional, defaults to `ansible_default_ipv4.address` if present)*

Defines an IPv4 address to use within any port redirection rule that does not contain a `bindaddress` value.

---

### `rinetd_default_ipv6_bindaddress`
#### *(optional, defaults to `ansible_default_ipv6.address` if present)*

Defines an IPv6 address to use within any port redirection rule that does not contain a `bindaddress` value.

---

> If a given redirection rule does not have `bindaddress` defined, and `rinetd_default_ipv4_bindaddress` along with `rinetd_default_ipv6_bindaddress` are both undefined or empty, then the rule is effectively skipped.
>
> Additionally, if `bindaddress` is undefined, and both `rinetd_default_ipv4_bindaddress` and `rinetd_default_ipv6_bindaddress` are defined, then two redirection rules would be generated - one per IP address.

---


### `rinetd_forwarding_rules`
#### *(required)*

Defines the various forwarding rules `rinetd` should follow.

- `comment` (optional): A comment denoting the purpose of a group of rules.
- `bindaddress` (optional): An IP address that `rinetd` should listen to for incoming traffic.
- `connectaddress`: An IP address that `rinetd` should redirect traffic to.
- `ports`: A list of port redirection rules that tell `rinetd` what ports to listen on and send traffic to.
  - `bindport`: A port number that `rinetd` should send traffic to on the remote host.
  - `connectport`: A port number that `rinetd` should listen to for incoming traffic.
  - `options` (optional, only in newer versions of `rinetd`): A dictionary of options that pertain to a particular rule. Any options defined will be added into the generated configuration, even outside the ones below.
    - `src`: If the host running `rinetd` has multiple network interfaces, the ensures that traffic is sent to a host over a specific interface.
    - `timeout`: Defines the maximum amount of time that the host that `rinetd` is listening for traffic from is allowed to not send any traffic, when the connection is UDP-based. After this point, `rinetd` will disconnect the remote host that it redirects traffic to, as to not exhaust resources. Defaults to `rinetd`'s default of 72 seconds if undefined.

---

> UDP, `bindport`, and `connectport`:
>
> You may optionally append `/udp` to listen for and/or UDP traffic with UDP-redirection-capable versions of `rinetd`. You may also mix these up, and receive UDP traffic but send it as TCP to the remote host.

---

### Example rule configuration

```yaml
rinetd_forwarding_rules:
  - comment: 'Redirect HTTP traffic from the default IPv4 and IPv6 addresses to 192.168.1.2'
    connectaddress: 192.168.1.2
    ports:
      - bindport: 80
        connectport: 80
  - comment: 'Redirect HTTP traffic from all interfaces to fe80::1'
    bindaddress: 0.0.0.0
    connectaddress: fe80::1
    ports:
      - bindport: 80
        connectport: 80
  - comment: 'Redirect UDP traffic from localhost on port 4000 to localhost on port 22 over TCP'
    bindaddress: 127.0.0.1
    connectaddress: 127.0.0.1
    ports:
      - bindport: 4000/udp
        connectport: 22
        options:
          timeout: 1200
  - comment: 'Redirect UDP traffic from localhost on port 8000 to 192.168.1.3, ensuring that the interface that has IP address 192.168.1.2 is used to send the traffic'
    bindaddress: 127.0.0.1
    connectaddress: 192.168.1.3
    ports:
      - bindport: 8000/udp
        connectport: 8000/udp
        options:
          src: 192.168.1.2
          timeout: 1200
```

Generated configuration, with a `rinetd_default_ipv4_bindaddress` of `192.168.1.1` and an undefined `rinetd_default_ipv6_bindaddress`:

```
# Redirect HTTP traffic from the default IPv4 and IPv6 addresses to 192.168.1.2
192.168.1.1   80      192.168.1.2     80

# Redirect HTTP traffic from all interfaces to fe80::1
0.0.0.0 80      fe80::1 80

# Redirect UDP traffic from localhost on port 4000 to localhost on port 22 over TCP
127.0.0.1       4000/udp        127.0.0.1       22      [timeout=1200]

# Redirect UDP traffic from localhost on port 8000 to 192.168.1.3, ensuring that the interface that has IP address 192.168.1.2 is used to se
nd the traffic
127.0.0.1       8000/udp        192.168.1.3     8000/udp        [src=192.168.1.2,timeout=1200]
```

---

### `rinetd_logging`
#### *(optional)*

Controls `rinetd`'s logging output.

- `enabled` (optional): Whether `rinetd` should set up its log file and log information to it.
- `logfile` (optional, defaults to `/var/log/rinetd.log`): The path to the log file.
- `logcommon` (optional): Whether `rinetd` should format its logs in a web server style log format.

---

Example Playbook
----------------

    - hosts: all
      become: yes
      vars:
        rinetd_forwarding_rules:
          - comment: 'Redirect HTTP traffic from the default IPv4 and IPv6 addresses to 192.168.1.2'
            connectaddress: 192.168.1.2
            ports:
              - bindport: 80
                connectport: 80
      roles:
         - kevinpoitra.rinetd

License
-------

BSD
