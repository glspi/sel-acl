import ipaddress
import re
from dataclasses import dataclass, field
import sys

import ciscoconfparse

ACL_RE_PATTERN = r"""
                ^\s+
                (
                (?P<remark>remark\s+.*)                                             # Remark
                |
                (
                (?P<action>permit|deny)\s+                                         # Action
                (?P<protocol>\S+)\s+                                                # Protocol
                (
                (?P<src_group>addrgroup\s\S+)                                       # Source addrgroup
                |(?P<src_wld>\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+)               # OR Source Network
                |(?P<src_host>host\s+\d+\.\d+\.\d+\.\d+)                            # OR 'host x.x.x.x'
                |(?P<src_any>any)                                                   # OR 'any'
                )
                (\s+)?
                (
                    (?P<src_portgroup>portgroup\s\S+)                                  # OR Source portgroup
                    |   
                    (
                        (?P<src_port_match>(eq|neq|precedence|range|tos|lt|gt)\s+)     # Source port Match ('eq' normally)
                        (
                        (?P<src_port_start>(?<=range\s)\S+)\s+(?P<src_port_end>\S+)         # Source port range 
                        |(?P<src_port>(?<!range\s)\S+)                                    # OR Source port (only)
                        )
                    )
                )?
                (\s+)   
                (
                (?P<dst_group>addrgroup\s\S+)                                       # Destination addrgroup
                |(?P<dst_wld>\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+)               # OR Destination Network
                |(?P<dst_host>host\s+\d+\.\d+\.\d+\.\d+)                            # OR 'host x.x.x.x'
                |(?P<dst_any>any)                                                   # OR 'any'
                )
                (?:\s+)?
                (
                    (?P<dst_portgroup>portgroup\s\S+)                                  # OR Destination portgroup
                    |
                    (
                        (?P<dst_port_match>(eq|neq|precedence|range|tos|lt|gt)\s+)     # Destination port Match ('eq' normally)
                        (
                        (?P<dst_port_start>(?<=range\s)\S+)\s+(?P<dst_port_end>\S+)         # Destination port range    
                        |(?P<dst_port>(?<!range\s)\S+)                                     # OR Destination port (only)
                        )
                    )
                )?
                (?:\s+)?
                (?P<flags_match>(match-any|match-all)\s+)?                             # match tcp flags
                (?P<tcp_flag>(((\+|-|)ack(\s*?)|(\+|-|)established(\s*?)|(\+|-|)fin(\s*?)|(\+|-|)fragments(\s*?)|(\+|-|)psh(\s*?)|(\+|-|)rst(\s*?)|(\+|-|)syn(\s*?)|urg(\s*?))+))?   # mostly just 'established'
                (?P<icmp_type>(administratively-prohibited|echo-reply|echo|mask-request|packet-too-big|parameter-problem|port-unreachable|redirect|router-advertisement|router-solicitation|time-exceeded|ttl-exceeded|unreachable))?    # icmp type
                (?P<log>(log-input|log))?                                               # log
                )
                )
                """


@dataclass()
class MigrationData:
    vlan_name: str
    acl_name_in: str
    acl_name_out: str
    tenant: str
    subnet: str


@dataclass()
class ACE:
    remark: str or None
    action: str or None
    protocol: str or None
    src_group: str or None
    src_wld: str or None
    src_host: str or None
    src_any: str or None
    src_portgroup: str or None
    src_port_match: str or None
    src_port_start: str or None
    src_port_end: str or None
    src_port: str or None
    dst_group: str or None
    dst_wld: str or None
    dst_host: str or None
    dst_any: str or None
    dst_portgroup: str or None
    dst_port_match: str or None
    dst_port_start: str or None
    dst_port_end: str or None
    dst_port: str or None
    flags_match: str or None
    tcp_flag: str or None
    icmp_type: str or None
    log: str or None

    # Custom/Created Variables
    src_cidr: str = field(default_factory=str)
    dst_cidr: str = field(default_factory=str)

    def __post_init__(self):
        # Initialize ACE in a more reusable way
        if self.remark:
            self.remark = self.remark.strip("remark ")
        if self.src_group:
            self.src_group = self.src_group.strip("addrgroup ")
        if self.src_host:
            self.src_host = self.src_host.strip("host ")
            if self.src_host not in ("0.0.0.0", "255.255.255.255"):
                self.src_host += "/32"
        if self.src_portgroup:
            self.src_portgroup = self.src_portgroup.strip("portgroup ")
        if self.dst_group:
            self.dst_group = self.dst_group.strip("addrgroup ")
        if self.dst_host:
            self.dst_host = self.dst_host.strip("host ")
            if self.dst_host not in ("0.0.0.0", "255.255.255.255"):
                self.dst_host += "/32"
        if self.dst_portgroup:
            self.dst_portgroup = self.dst_portgroup.strip("portgroup ")

        # Create CIDR if needed
        try:
            if not self.src_any and self.src_wld:
                src_net, src_wildcard = self.src_wld.split()
                self.src_cidr = (
                    src_net
                    + "/"
                    + str(ipaddress.ip_network(src_net + "/" + src_wildcard).prefixlen)
                )
            if not self.dst_any and self.dst_wld:
                dst_net, dst_wildcard = self.dst_wld.split()
                self.dst_cidr = (
                    dst_net
                    + "/"
                    + str(ipaddress.ip_network(dst_net + "/" + dst_wildcard).prefixlen)
                )
        except ValueError as e:
            if "has host bits set" in str(e):
                print("ACL is 'incorrect', host bits are set in network, CIDR could not be created.")
                print(self)

    def output_cidr(self):
        if self.remark:
            return " " + self.remark + "\n"

        output = " "
        output += f"{self.action} {self.protocol} "

        # SOURCE ADDRESS
        if self.src_group:
            output += f"addrgroup {self.src_group} "
        elif self.src_any:
            output += "any "
        elif self.src_host:
            output += f"{self.src_host} "
        elif self.src_cidr:
            output += f"{self.src_cidr} "
        else:
            print(f"Error, no source found in ACE {self}.")
            sys.exit()
        # SOURCE PORT
        if self.src_portgroup:
            output += f"portgroup {self.src_portgroup} "
        elif self.src_port_match:
            output += f"{self.src_port_match} "
        if self.src_port_start and self.src_port_end:
            output += f"{self.src_port_start} + {self.src_port_end} "
        elif self.src_port:
            output += f"{self.src_port} "

        # DESTINATION
        if self.dst_group:
            output += f"addrgroup {self.dst_group} "
        elif self.dst_any:
            output += "any "
        elif self.dst_host:
            output += f"{self.dst_host} "
        elif self.dst_cidr:
            output += f"{self.dst_cidr} "
        else:
            print(f"Error, no destination found in ACE {self}.")
            sys.exit()
        # DESTINATION PORT
        if self.dst_portgroup:
            output += f"portgroup {self.dst_portgroup} "
        elif self.dst_port_match:
            output += f"{self.dst_port_match} "
        if self.dst_port_start and self.dst_port_end:
            output += f"{self.dst_port_start} + {self.dst_port_end} "
        elif self.dst_port:
            output += f"{self.dst_port} "

        # EXTRAS (flags/icmp/log)
        if self.flags_match:
            output += f"{self.flags_match} "
        if self.tcp_flag:
            output += f"{self.tcp_flag} "
        if self.icmp_type:
            output += f"{self.icmp_type} "
        if self.log:
            output += f"{self.log} "

        return output + "\n"


@dataclass()
class ACL:
    name: str
    acl: ciscoconfparse.models_cisco.IOSCfgLine
    aces: list[ACE] = field(default_factory=list)
    rec = re.compile(ACL_RE_PATTERN, re.X)

    def __post_init__(self):
        if self.acl:
            for child in self.acl.children:
                results = self.rec.search(child.text)
                if not results:
                    print(child.text)
                    print("^^ERROR WITH ABOVE LINE:^^")
                else:
                    ace = ACE(**results.groupdict())
                    self.aces.append(ace)

    def __contains__(self, find_ace):
        for ace in self.aces:
            if ace == find_ace:
                return True

    def output_cidr(self, name: str):
        output = f"ip access-list {name}\n"
        for ace in self.aces:
            output += ace.output_cidr()
        return output
