#!/usr/bin/python
from ansible.errors import AnsibleFilterError


class FilterModule(object):
    def filters(self):
        return {
            'rinetd_format_rule': rinetd_format_rule,
        }


def rinetd_format_rule(args):
    rule = args['rule']
    port = args['port']
    default_ipv4_address = args['default_ipv4']
    default_ipv6_address = args['default_ipv6']
    bind_address = rule.get('bindaddress')
    bind_port = port.get('bindport')
    connect_address = rule.get('connectaddress')
    connect_port = port.get('connectport')
    options = port.get('options')

    if bind_port is None:
        raise AnsibleFilterError('A forwarding rule does not have ''bindport'' defined!')

    if connect_address is None:
        raise AnsibleFilterError('A forwarding rule does not have ''connect_address'' defined!')

    if connect_port is None:
        raise AnsibleFilterError('A forwarding rule does not have ''connect_port'' defined!')

    if bind_address is None:
        # No bind address was defined for this forwarding rule.
        # Instead, let's generate two rules, one with the default IPv4 address,
        # and another with the default IPv6 address.
        if not default_ipv4_address and not default_ipv6_address:
            raise AnsibleFilterError('A forwarding rule does not have a bind address defined while there are also '
                                     'no default IPv4 and IPv6 bind addresses!')

        if default_ipv4_address:
            rule = generate_rule(default_ipv4_address, bind_port, connect_address, connect_port, options)

        if default_ipv6_address:
            if default_ipv4_address:
                rule += '\r\n'

            rule += generate_rule(default_ipv6_address, bind_port, connect_address, connect_port, options)

        return rule
    else:
        return generate_rule(bind_address, bind_port, connect_address, connect_port, options)


def generate_rule(bind_address, bind_port, connect_address, connect_port, options):
    rule = str(bind_address) + '\t' + str(bind_port) + '\t' + str(connect_address) + '\t' + str(connect_port)

    if options:
        rule += '\t'
        rule += '['
        rule += ",".join("=".join((str(k), str(v))) for k, v in options.items())
        rule += ']'

    return rule
