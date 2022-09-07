import textfsm
from sel_acl.objs import ACE, ACL
from sel_acl.utils import get_acl, get_acl2
from ciscoconfparse import CiscoConfParse
from rich.pretty import pprint
import re

test_acl_correct = ACL(
    name="my-test-acl",
    aces=[
        ACE(
            action="",
            protocol="",
            src_host="",
            src_any="",
            src_network="",
            src_wildcard="",
            src_network_object_group_name="",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="",
            dst_network="",
            dst_wildcard="",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="### MY REMARK",
        ),
        ACE(
            action="permit",
            protocol="ip",
            src_host="",
            src_any="",
            src_network="10.0.0.0",
            src_wildcard="0.255.255.255",
            src_network_object_group_name="",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="",
            dst_network="10.1.0.0",
            dst_wildcard="0.255.255.255",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="tcp",
            src_host="",
            src_any="",
            src_network="10.0.0.0",
            src_wildcard="0.255.255.255",
            src_network_object_group_name="",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="",
            dst_network="10.1.0.0",
            dst_wildcard="0.255.255.255",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="udp",
            src_host="",
            src_any="",
            src_network="10.0.0.0",
            src_wildcard="0.255.255.255",
            src_network_object_group_name="",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="",
            dst_network="10.1.0.0",
            dst_wildcard="0.255.255.255",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="icmp",
            src_host="",
            src_any="",
            src_network="10.0.0.0",
            src_wildcard="0.255.255.255",
            src_network_object_group_name="",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="",
            dst_network="10.1.0.0",
            dst_wildcard="0.255.255.255",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="tcp",
            src_host="",
            src_any="",
            src_network="10.0.0.0",
            src_wildcard="0.255.255.255",
            src_network_object_group_name="",
            src_port_match="eq",
            src_port="443",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="",
            dst_network="10.1.0.0",
            dst_wildcard="0.255.255.255",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="tcp",
            src_host="",
            src_any="",
            src_network="10.0.0.0",
            src_wildcard="0.255.255.255",
            src_network_object_group_name="",
            src_port_match="eq",
            src_port="443",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="",
            dst_network="10.1.0.0",
            dst_wildcard="0.255.255.255",
            dst_network_object_group_name="",
            dst_port_match="eq",
            dst_port="443",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="ip",
            src_host="10.10.10.10",
            src_any="",
            src_network="",
            src_wildcard="",
            src_network_object_group_name="",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="11.11.11.11",
            dst_any="",
            dst_network="",
            dst_wildcard="",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="log",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="deny",
            protocol="ip",
            src_host="",
            src_any="any",
            src_network="",
            src_wildcard="",
            src_network_object_group_name="",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="",
            dst_any="any",
            dst_network="",
            dst_wildcard="",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="log",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="udp",
            src_host="0.0.0.0",
            src_any="",
            src_network="",
            src_wildcard="",
            src_network_object_group_name="",
            src_port_match="eq",
            src_port="bootpc",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="",
            dst_host="255.255.255.255",
            dst_any="",
            dst_network="",
            dst_wildcard="",
            dst_network_object_group_name="",
            dst_port_match="eq",
            dst_port="bootps",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
        ACE(
            action="permit",
            protocol="tcp",
            src_host="",
            src_any="",
            src_network="",
            src_wildcard="",
            src_network_object_group_name="source_object_group",
            src_port_match="",
            src_port="",
            src_port_range_start="",
            src_port_range_end="",
            src_portgroup_name="source_portgroup",
            dst_host="8.8.8.8",
            dst_any="",
            dst_network="",
            dst_wildcard="",
            dst_network_object_group_name="",
            dst_port_match="",
            dst_port="",
            dst_port_range_start="",
            dst_port_range_end="",
            dst_portgroup_name="",
            service_object_group_name="",
            flags_match="",
            tcp_flag="",
            log="",
            log_tag="",
            icmp_type="",
            time="",
            state="",
            matches="",
            remark="",
        ),
    ],
)


def test_textfsm():
    with open("./tests/acl_tests.txt", "r") as fin:
        acl_str = fin.read()
    acl_parser = CiscoConfParse("./tests/acl_tests.txt")

    test_acl = get_acl("my-test-acl", acl_parser)
    assert test_acl == test_acl_correct

def test_regex():
    with open("acl_tests.txt", "r") as fin:
        acl_str = fin.read()
    acl_parser = CiscoConfParse("acl_tests.txt")

    test_acl = get_acl2("my-test-acl", acl_parser)

    pprint(test_acl)

def etest2():
    def blah(mydict):
        mynewdict = {}
        for k,v in mydict.items():
            if v:
                mynewdict.update({k:v})
        return mynewdict

    teststr = "permit ip 5.5.5.5 6.6.6.6 eq 383 1.1.1.1 0.0.255.255"
    teststr2 = "permit tcp addrgroup hi 2.2.2.0 0.0.0.255"
    #teststr2 = "permit tcp addrgroup hi any eq 5"
    teststr0 = "permit tcp addrgroup hi addrgroup hi2"
    teststr11 = "permit tcp host 10.10.101.10 host 9.9.9.9"
    teststr3 = "permit tcp addrgroup hi portgroup ports 2.2.2.0 0.0.0.255"
    teststr4 = "permit udp any any"
    teststr5 = "permit ip 5.5.5.5 6.6.6.6 range 500 600 addrgroup sheesh"
    teststr6 = "permit ip 5.5.5.5 6.6.6.6 range 500 600 6.6.6.6 0.0.0.255"
    teststr7 = "permit ip host 1.1.1.1 5.5.5.5 6.6.6.6 eq 686"
    teststr8 = "permit ip 5.5.5.5 6.6.6.6 eq 686 host 2.2.2.2"
    teststr9 = "permit tcp addrgroup source_object_group portgroup source_portgroup host 8.8.8.8"
    teststr10 = "permit tcp addrgroup source_object_group portgroup source_portgroup host 8.8.8.8 established"
    teststr20 = "permit icmp any any echo-reply"
    re_pattern = r"""
                ^\s+(?P<action>permit|deny)\s+                                         # Action
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
                """

    rec = re.compile(re_pattern, re.X)

    for test in (teststr, teststr2, teststr0, teststr11, teststr3, teststr4, teststr5, teststr6, teststr7, teststr8, teststr9, teststr10, teststr20):
        res = rec.search(test)
        if res:
            print(blah(res.groupdict()))
        else:
            print('failed:', test)


if __name__ == "__main__":
    #test_textfsm()
    test_regex()
