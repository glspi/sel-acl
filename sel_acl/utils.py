import re
import sys
from ipaddress import ip_network
from typing import Dict, List

from ciscoconfparse import CiscoConfParse
from rich.pretty import pprint

from sel_acl.objs import ACE, ACL, CustomWorksheet, MigrationData


def get_acl_from_file(filename: str, name: str):
    acl_parser = CiscoConfParse(filename)
    search_for = rf"ip access-list extended {name}"

    try:
        my_acl = ACL(name=name, acl=acl_parser.find_objects(search_for)[0])
    except IndexError:
        print(f"Error loading acl: '{name}' from {filename}, not found?")
        my_acl = ACL(name=f"DID NOT FIND {name}")

    return my_acl


def get_addrgroups_from_file(filename: str) -> Dict:
    addr_group_parser = CiscoConfParse(filename)
    search_for = r"object-group ip address"

    addr_groups = {}
    group_names = addr_group_parser.find_objects(search_for)
    for group in group_names:
        match = re.match(r"object-group\sip\saddress\s(.+)", group.text)
        if match:
            name = match.group(1).strip()
            addr_groups[name] = []
            for host in group.children:
                match = re.match(r"\shost-info\s(.+)", host.text)
                if not match:
                    match = re.match(
                        r"\s(\d+\.\d+\.\d+\.\d+)\s(\d+\.\d+\.\d+\.\d+)(?:\s+)?",
                        host.text,
                    )
                    if match:
                        subnet, mask = match.groups()
                        network = str(ip_network(f"{subnet}/{mask}", strict=False))
                        addr_groups[name].append(network)
                else:
                    ip = match.group(1).strip() + "/32"
                    addr_groups[name].append(ip)

    return addr_groups


def get_initial_data(excel_filename: str, vlan: int):
    # Get ACL/Name/Subnet/Etc from Vlan Number
    ws = CustomWorksheet(excel_filename=excel_filename)
    my_row = ws.find_row_from_vlan(vlan)
    mig_data = ws.get_migration_data_from_row(my_row)

    # pprint(mig_data)
    return ws, mig_data


def run_main(excel_filename: str, vlan: int, acls: str, addrgroups: str, nsew: str):

    # Set initial data
    ws, mig_data = get_initial_data(excel_filename=excel_filename, vlan=vlan)
    addr_groups = get_addrgroups_from_file(addrgroups)

    # Get Existing ACL in/out
    acl_in = get_acl_from_file(filename=acls, name=mig_data.acl_name_in)
    acl_out = get_acl_from_file(filename=acls, name=mig_data.acl_name_out)

    if nsew == "cidr":
        print("CIDR Output..")
        print("--------------")
        new_acl_in = acl_in.output_cidr(name=f"New-NS-{acl_in.name}")
        new_acl_out = acl_out.output_cidr(name=f"New-NS-{acl_out.name}")
        print(new_acl_in)
        print(new_acl_out)

    if nsew == "ew":
        print("East/West...")
        print("--------------")
        ew_mig_data = ws.get_tenant_rows(tenant=mig_data.tenant)
        # pprint(ew_mig_data)

        ew_aces = ew_checker(
            ew_mig_data=ew_mig_data, acl=acl_in, addr_groups=addr_groups
        )

        for ace in ew_aces:
            contract = ace.to_contract(mig_data)
            print(contract)

    if nsew == "ns":
        print("North/South...")
        print("--------------")
        ew_mig_data = ws.get_tenant_rows(tenant=mig_data.tenant)
        ew_aces = ew_checker(
            ew_mig_data=ew_mig_data, acl=acl_in, addr_groups=addr_groups
        )

        for ace in ew_aces:
            if ace in acl_in.aces:
                index = acl_in.aces.index(ace)
                acl_in.aces.insert(
                    index,
                    ACE(
                        remark=f"### BELOW WILL BE EAST/WEST, REMOVE ME: {ace.output_cidr()}"
                    ),
                )
                # contract = ace.to_contract(mig_data)

        new_acl_in = acl_in.output_cidr(name=f"New-NS-{acl_in.name}")
        new_acl_out = acl_out.output_cidr(name=f"New-NS-{acl_out.name}")
        print(new_acl_in)
        print(new_acl_out)


def ew_checker(
    ew_mig_data: List[MigrationData], acl: ACL, addr_groups: Dict[str, List[str]]
):
    ew_aces = []
    for mig_data in ew_mig_data:
        if mig_data.subnet is not None:
            try:
                subnet = ip_network(mig_data.subnet, strict=False)
            except ValueError as e:
                print(f"\t\tError with vlan: {mig_data.vlan_name} in excel: ")
                print(f"\t\t\t{e}\n")
                continue

        for ace in acl.aces:
            if ace.remark:
                continue

            dest_in = ace.destination_in(subnet, addr_groups)

            if dest_in == "subnet":
                print(f"{mig_data.vlan_name} vlan/subnet matches destination: {subnet}")
                ew_aces.append(ace)
            if dest_in == "addr_group":
                print(
                    f"{mig_data.vlan_name} vlan/subnet matches ADDRESS GROUP!: {subnet}"
                )
                ew_aces.append(ace)
            # if dest_in == "supernet":
            #     print(f"{mig_data.vlan_name} vlan/subnet is a subnet of destination: {subnet}...what to do?!")
            #     print(ace.to_contract(mig_data))
    return ew_aces


# def get_all_acls(ws: CustomWorksheet, acls:str) -> Dict:
#     all_acls = {None: ACL(name='none')}
#     all_acl_names_in = ws.get_rows_from_column(column="ACCESS-LIST-IN")
#     for name in all_acl_names_in:
#         acl = get_acl_from_file(filename=acls, name=name)
#         # if "DID NOT FIND" in acl.name:
#         #     acl = ACL(name="DID NOT FIND")
#         if not all_acls.get(name):
#             all_acls[name] = acl
#
#     return all_acls
