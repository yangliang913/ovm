import calendar
import inspect
import netaddr
import os
import pprint
import tg
from stackone.core.utils.utils import to_str
import stackone.core.utils.constants as constants
import gettext
_ = gettext.gettext
import logging
LOG = logging.getLogger('stackone.core.utils')
def _bin_file(script):
    return os.path.abspath(os.path.join(__file__, '../../../bin', script))

class IptablesRule(object):
    def __init__(self, chain, rule, wrap=True, top=False):
        self.chain = chain
        self.rule = rule
        self.wrap = wrap
        self.top = top

    def __eq__(self, other):
        if self.chain == other.chain and self.rule == other.rule and self.top == other.top:
            return self.chain == other.chain

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        if self.wrap:
            chain = '%s-%s' % (constants.FW_CHAIN_NAME, self.chain)
        else:
            chain = self.chain
        return '-A %s %s' % (chain, self.rule)

class IptablesTable(object):
    def __init__(self):
        self.rules = []
        self.chains = set()
        self.unwrapped_chains = set()

    def add_chain(self, name, wrap=True):
        if wrap:
            self.chains.add(name)
        else:
            self.unwrapped_chains.add(name)

    def remove_chain(self, name, wrap=True):
        if wrap:
            chain_set = self.chains
        else:
            chain_set = self.unwrapped_chains
        if name not in chain_set:
            LOG.debug(_('Attempted to remove chain %s which does not exist'), name)
            return None
        chain_set.remove(name)
        self.rules = filter((lambda r: r.chain != name), self.rules)
        if wrap:
            jump_snippet = '-j %s-%s' % (constants.FW_CHAIN_NAME, name)
        else:
            jump_snippet = '-j %s' % (name)
        self.rules = filter((lambda r: jump_snippet not in r.rule), self.rules)


    def add_rule(self, chain, rule, wrap=True, top=False):
        if wrap and chain not in self.chains:
            raise ValueError(_('Unknown chain: %r') % chain)
        if '$' in rule:
            rule = ' '.join(map(self._wrap_target_chain, rule.split(' ')))
        self.rules.append(IptablesRule(chain, rule, wrap, top))



    def _wrap_target_chain(self, s):
        if s.startswith('$'):
            return '%s-%s' % (constants.FW_CHAIN_NAME, s[1:])
        return s


    def remove_rule(self, chain, rule, wrap=True, top=False):
        try:
            r = IptablesRule(chain, rule, wrap, top)
            while r in self.rules:
                self.rules.remove(r)
        except ValueError:
            LOG.info('Tried to remove rule that was not there: %(chain)r %(rule)r %(wrap)r %(top)r' %{'chain':chain,'rule':rule,'top':top,'wrap':wrap})


    def empty_chain(self, chain, wrap=True):
        chained_rules = [rule for rule in self.rules if rule.chain == chain and rule.wrap == wrap]
        for rule in chained_rules:
            self.rules.remove(rule)


    def dump(self):
        for r in self.rules:
            print str(r)
        pprint.pprint(self.chains)
        pprint.pprint(self.unwrapped_chains)


class IptablesManager(object):
    def __init__(self, context):
        self.set_chain_name(context)
        self.ipv4 = {'filter':IptablesTable(),'nat':IptablesTable()}
        self.ipv6 = {'filter':IptablesTable()}
        self.nw_service_host = None
        for tables in [self.ipv4, self.ipv6]:
            tables['filter'].add_chain('stackone-filter-top', wrap=False)
            tables['filter'].add_rule('FORWARD', '-j stackone-filter-top', wrap=False, top=True)
            tables['filter'].add_rule('OUTPUT', '-j stackone-filter-top', wrap=False, top=True)
            tables['filter'].add_chain('local')
            tables['filter'].add_rule('stackone-filter-top', '-j $local', wrap=False)

        #builtin_chains = {6:{'filter':['INPUT','OUTPUT','FORWARD']},4:{'nat':['PREROUTING','OUTPUT','POSTROUTING']}}
        builtin_chains = {4: {'filter': ['INPUT', 'OUTPUT', 'FORWARD'], 'nat': ['PREROUTING', 'OUTPUT', 'POSTROUTING']}, 6: {'filter': ['INPUT', 'OUTPUT', 'FORWARD']}}
        for ip_version in builtin_chains:
            if ip_version == 4:
                tables = self.ipv4
            elif ip_version == 6:
                tables = self.ipv6
            for table,chains in builtin_chains[ip_version].iteritems():
                for chain in chains:
                    tables[table].add_chain(chain)
                    tables[table].add_rule(chain, '-j $%s' % (chain), wrap=False)
        self.ipv4['nat'].add_chain('stackone-postrouting-bottom', wrap=False)
        self.ipv4['nat'].add_rule('POSTROUTING', '-j stackone-postrouting-bottom', wrap=False)
        self.ipv4['nat'].add_chain('snat')
        self.ipv4['nat'].add_rule('stackone-postrouting-bottom', '-j $snat', wrap=False)
        self.ipv4['nat'].add_chain('floating-snat')
        self.ipv4['nat'].add_rule('snat', '-j $floating-snat')


    def set_nw_service_host(self, nw_service_host):
        if self.nw_service_host == None:
            self.nw_service_host = nw_service_host
        else:
            LOG.info('Changing nw_service_host from %s to %s\n', (self.nw_service_host, nw_service_host))
            self.nw_service_host = nw_service_host
            self.apply()


    def execute(self, cmd, params=None, attempts=1L):
        if self.nw_service_host:
            out,code = self.nw_service_host.node_proxy.exec_cmd(cmd=cmd, timeout=60, params=params)
            return (out, code)
        LOG.error('Firewall execute called without any network service host')
        raise Exception('Firewall execute called without any network service host')


    def apply(self):
        s = [('iptables', self.ipv4)]
        if False:
            s += [('ip6tables', self.ipv6)]
        for cmd,tables in s:
            for table in tables:
                current_table,_ = self.execute('%s-save' % (cmd) + ' -t' + ' %s' % (table), attempts=5)
                c_lines = current_table.split('\n')
                current_lines = []
                for l in c_lines:
                    current_lines.append(l.strip())
                new_filter = self._modify_rules(current_lines, tables[table])
                print new_filter,'#############new_filter#############'
                out,code = self.execute('%s-restore' % (cmd), params=new_filter, attempts=5)
                print out,code,'######out,code#####'
                if code != 0:
                    LOG.error('ERROR : apply failed. :' + out)
                    LOG.error('ERROR : apply failed. PARAMS:' + str(new_filter))

#################
    def _modify_rules(self, current_lines, table, binary=None):
        unwrapped_chains = table.unwrapped_chains
        chains = table.chains
        rules = table.rules
        new_filter = filter((lambda line: constants.FW_CHAIN_NAME not in line), current_lines)
        seen_chains = False
        rules_index = 0
        for rules_index, rule in enumerate(new_filter):
            if not seen_chains:
                if rule.startswith(':'):
                    seen_chains = True
            elif not rule.startswith(':'):
                break
        
        our_rules = []
        for rule in rules:
            rule_str = str(rule)
            if rule.top:
                new_filter = filter((lambda s: s.strip() != rule_str.strip()), new_filter)
            our_rules += [rule_str]
    
        new_filter[rules_index:rules_index] = our_rules
        new_filter[rules_index:rules_index] = [':%s - [0:0]' % (name) for name in unwrapped_chains]
        new_filter[rules_index:rules_index] = [':%s-%s - [0:0]' % (constants.FW_CHAIN_NAME, name) for name in chains ]
        seen_lines = set()
        def _weed_out_duplicates(line):
            line = line.strip()
            if line in seen_lines:
                return False
            seen_lines.add(line)
            return True
        
        new_filter.reverse()
        new_filter = filter(_weed_out_duplicates, new_filter)
        new_filter.reverse()
        return new_filter


    def init_host(self):
        self.add_dhcp_bootp_rules()

    def dhcp_bootp_rules(self):
        return [(self.ipv4['filter'], 'INPUT', '-p tcp --dport 67 -j ACCEPT'), (self.ipv4['filter'], 'INPUT', '-p udp --dport 67 -j ACCEPT'), (self.ipv4['filter'], 'INPUT', '-p tcp --dport 53 -j ACCEPT'), (self.ipv4['filter'], 'INPUT', '-p udp --dport 53 -j ACCEPT')]

    def add_dhcp_bootp_rules(self):
        for table,chain,rule in self.dhcp_bootp_rules():
            table.add_rule(chain, rule, wrap=True)
        self.apply()


    def remove_dhcp_bootp_rules(self):
        for table,chain,rule in self.dhcp_bootp_rules():
            table.remove_rule(chain, rule, wrap=True)
        self.apply()


    def ensure_network_isolation(self, nw_if):
        self.ipv4['filter'].add_rule('FORWARD', '-i %s ! -o %s -j REJECT --reject-with icmp-port-unreachable' % (nw_if, nw_if))
        self.apply()

    def remove_network_isolation(self, nw_if):
        self.ipv4['filter'].remove_rule('FORWARD', '-i %s ! -o %s -j REJECT --reject-with icmp-port-unreachable' % (nw_if, nw_if))
        self.apply()

    def ensure_network_nating(self, private_nw_if, private_nw_cidr, public_if):
        for table,chain,rule in self.nating_rules(private_nw_if, private_nw_cidr, public_if):
            table.add_rule(chain, rule)
        self.apply()


    def remove_network_nating(self, private_nw_if, private_nw_cidr, public_if):
        for table,chain, rule in self.nating_rules(private_nw_if, private_nw_cidr, public_if):
            table.remove_rule(chain, rule)
        self.apply()


    def nating_rules(self, private_nw_if, private_nw_cidr, public_if):
        return [(self.ipv4['nat'], 'POSTROUTING', '-s %s -o %s -j MASQUERADE' % (private_nw_cidr, public_if)), (self.ipv4['filter'], 'FORWARD', '-i %s -o %s -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT' % (public_if, private_nw_if)), (self.ipv4['filter'], 'FORWARD', '-i %s -o %s -j ACCEPT' % (private_nw_if, public_if))]

    def ensure_floating_forward(self, floating_ip, fixed_ip):
        for chain,rule in self.floating_forward_rules(floating_ip, fixed_ip):
            self.ipv4['nat'].add_rule(chain, rule)
        self.apply()


    def remove_floating_forward(self, floating_ip, fixed_ip):
        for chain,rule in self.floating_forward_rules(floating_ip, fixed_ip):
            self.ipv4['nat'].remove_rule(chain, rule)
        self.apply()


    def floating_forward_rules(self, floating_ip, fixed_ip):
        return [('PREROUTING', '-d %s -j DNAT --to %s' % (floating_ip, fixed_ip)), ('OUTPUT', '-d %s -j DNAT --to %s' % (floating_ip, fixed_ip)), ('floating-snat', '-s %s -j SNAT --to %s' % (fixed_ip, floating_ip))]

    def set_chain_name(self, context):
        binary_name = 'stackone-nw'
        if tg.config.get('fw_namespace') in constants.TRUE_CHECK:
            if context:
                if context.find(' ') >= 0L:
                    context = context.replace(' ', '_')
                constants.FW_CHAIN_NAME = to_str(binary_name) + '-' + to_str(context)
            else:
                constants.FW_CHAIN_NAME = to_str(binary_name)
        else:
            constants.FW_CHAIN_NAME = to_str(binary_name)






