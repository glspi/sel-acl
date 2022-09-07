from dataclasses import dataclass, field

@dataclass()
class MigrationData:
    vlan_name: str
    acl_name_in: str
    acl_name_out: str
    tenant: str
    subnet: str


@dataclass()
class ACE2:
    remark: str
    action: str
    protocol: str
    src_group: str
    src_wld: str
    src_host: str
    src_any: str
    src_portgroup: str
    src_port_match: str
    src_port_start: str
    src_port_end: str
    src_port: str
    dst_group: str
    dst_wld: str
    dst_host: str
    dst_any: str
    dst_portgroup: str
    dst_port_match: str
    dst_port_start: str
    dst_port_end: str
    dst_port: str
    flags_match: str
    tcp_flag: str
    icmp_type: str
    log: str


@dataclass()
class ACE:
    action: str
    protocol: str
    src_host: str
    src_any: str
    src_network: str
    src_wildcard: str
    src_network_object_group_name: str
    src_port_match: str
    src_port: str
    src_port_range_start: str
    src_port_range_end: str
    src_portgroup_name: str
    dst_host: str
    dst_any: str
    dst_network: str
    dst_wildcard: str
    dst_network_object_group_name: str
    dst_port_match: str
    dst_port: str
    dst_port_range_start: str
    dst_port_range_end: str
    dst_portgroup_name: str
    service_object_group_name: str
    flags_match: str
    tcp_flag: str
    log: str
    log_tag: str
    icmp_type: str
    time: str
    state: str
    matches: str
    remark: str


@dataclass()
class ACL:
    name: str
    aces: list[ACE2] = field(default_factory=list)
