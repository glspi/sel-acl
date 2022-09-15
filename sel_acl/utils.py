"""sel_acl.utils"""
import re
import sys
from ipaddress import ip_network
from typing import Dict, List

from ciscoconfparse import CiscoConfParse
from openpyxl.workbook.views import BookView
from openpyxl.workbook.workbook import Workbook

from sel_acl.objs import ACE, ACL, CustomWorksheet, MigrationData


def get_acl_from_file(filename: str, name: str):
    if name == "" or name is None:
        return None

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


def get_initial_data(excel_filename: str, vlan: int, addr_groups: str):
    # Get ACL/Name/Subnet/Etc from Vlan Number
    ws = CustomWorksheet(excel_filename=excel_filename)
    my_row = ws.find_row_from_vlan(vlan)
    mig_data = ws.get_migration_data_from_row(my_row)

    if not mig_data:
        print(
            f"We aren't migrating this vlan ({vlan}) or it has no subnet! (check the spreadsheet.)"
        )
        sys.exit()

    addr_groups = get_addrgroups_from_file(addr_groups)
    return ws, mig_data, addr_groups


def remove_self(vlan_name: str, ew_mig_data: List[MigrationData]):
    ew_mig_data2 = []
    for mig_data in ew_mig_data:
        if mig_data.vlan_name != vlan_name:
            ew_mig_data2.append(mig_data)
    return ew_mig_data2


def print_cidr_acls(acl_in, acl_out):
    new_acl_in = acl_in.output_cidr(name=f"New-NS-{acl_in.name}")
    new_acl_out = acl_out.output_cidr(name=f"New-NS-{acl_out.name}")
    print(new_acl_in)
    print(new_acl_out)


def ns_ew_combined(ws, mig_data, acl, addr_groups, direction: str = "in"):
    ew_mig_data = ws.get_tenant_rows(tenant=mig_data.tenant)
    if ew_mig_data:
        ew_mig_data = remove_self(vlan_name=mig_data.vlan_name, ew_mig_data=ew_mig_data)

        ew_aces, ew_contracts, ew_supernets = ew_checker(
            ew_mig_data=ew_mig_data,
            acl=acl,
            addr_groups=addr_groups,
            my_mig_data=mig_data,
            direction=direction,
        )
        if ew_supernets:
            print("\n\nSupernet rules found:")
            print(f"{'Overlapping VLAN':<60}:\t{' ACE Entry'}")
            print(
                "----------------------------------------------------------------------------------------"
            )
            for supernet in ew_supernets:
                for vlan_name, ace in supernet.items():
                    print(f"{vlan_name:<60}:\t{ace.output_cidr()}")

        return ew_aces, ew_contracts


def create_contracts(ew_aces, ew_contracts, acl, filename):
    print(f"\n\nEast/West Contracts found in {acl.name}:")
    print("---------------------")
    if ew_contracts:
        for ace in ew_aces:
            if ace in acl.aces:
                print(ace.output_cidr())
        create_contract_file(contracts=ew_contracts, filename=filename)


def print_and_remark_acl(ew_aces, acl):
    # Insert remarks so we can find these to delete after migrations
    for ace in ew_aces:
        if ace in acl.aces:
            index = acl.aces.index(ace)
            acl.aces.insert(
                index,
                ACE(
                    remark=f"### EAST/WEST BELOW, REMOVE ME LATER: {ace.output_cidr()}"
                ),
            )

    if ew_aces:
        print(f"\n\nEast/West Rules found in {acl.name}:")
        print("---------------------")
        for ace in ew_aces:
            if ace in acl.aces:
                print(ace.output_cidr())

    new_acl = acl.output_cidr(name=f"New-NS-{acl.name}")
    print("\n\nNew North/South ACL:\n")
    print("---------------------")
    print(new_acl)


def run_main(excel_filename: str, vlan: int, acls: str, addr_groups: str, nsew: str):

    # Set initial data
    ws, mig_data, addr_groups = get_initial_data(
        excel_filename=excel_filename, vlan=vlan, addr_groups=addr_groups
    )

    # Get Existing ACL in/out
    acl_in = get_acl_from_file(filename=acls, name=mig_data.acl_name_in)
    acl_out = get_acl_from_file(filename=acls, name=mig_data.acl_name_out)

    if not acl_in:
        print(f"Error, no access-list found for vlan {vlan}: {mig_data.vlan_name}")
        sys.exit()

    if nsew == "cidr":
        print("CIDR Output..")
        print("--------------")
        print_cidr_acls(acl_in, acl_out)

    if nsew == "ew":
        print("East/West...")
        print("--------------")
        ew_aces, ew_contracts = ns_ew_combined(
            ws=ws, mig_data=mig_data, addr_groups=addr_groups, acl=acl_in
        )
        create_contracts(
            ew_aces=ew_aces,
            ew_contracts=ew_contracts,
            acl=acl_in,
            filename=f"contracts-{mig_data.vlan_name}-in.xlsx",
        )

        ew_aces, ew_contracts = ns_ew_combined(
            ws=ws, mig_data=mig_data, addr_groups=addr_groups, acl=acl_out
        )
        create_contracts(
            ew_aces=ew_aces,
            ew_contracts=ew_contracts,
            acl=acl_out,
            filename=f"contracts-{mig_data.vlan_name}-out.xlsx",
        )

    if nsew == "ns":
        print("North/South...")
        print("--------------")

        ew_aces, _ = ns_ew_combined(
            ws=ws, mig_data=mig_data, addr_groups=addr_groups, acl=acl_in
        )
        print_and_remark_acl(ew_aces=ew_aces, acl=acl_in)

        ew_aces, _ = ns_ew_combined(
            ws=ws, mig_data=mig_data, addr_groups=addr_groups, acl=acl_out
        )
        print_and_remark_acl(ew_aces=ew_aces, acl=acl_out)


def create_contract_file(filename: str, contracts: List[Dict[str, str]]):
    wb = Workbook()
    ws = wb.active
    headers = []
    for k, v in contracts[0].items():
        headers.append(k)
    ws.append(headers)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    view = [BookView(xWindow=0, yWindow=0, windowWidth=18140, windowHeight=15540)]
    wb.views = view
    # Get headers and put into dict so that sheet["headername"] = "column_letter"
    col_dict = {}
    for col in ws.iter_cols(1, ws.max_column):
        col_dict[col[0].value.upper()] = col[0].column_letter

    for contract in contracts:
        cell_dict = {}
        for header, value in contract.items():
            cell_dict[col_dict[header.upper()]] = value
        ws.append(cell_dict)

    wb.save(filename)
    print(f"\nContracts saved at '{filename}'.")


def ew_checker(
    ew_mig_data: List[MigrationData],
    acl: ACL,
    addr_groups: Dict[str, List[str]],
    my_mig_data: MigrationData,
    direction: str = "in",
):
    ew_aces = []
    ew_contracts = []
    ew_supernets = []
    for mig_data in ew_mig_data:
        for ace in acl.aces:
            if ace.remark:
                continue
            for subnet in mig_data.subnet:
                if direction == "in":
                    src_dest_in = ace.destination_in(
                        ip_network(subnet, strict=False), addr_groups
                    )
                else:
                    src_dest_in = ace.source_in(
                        ip_network(subnet, strict=False), addr_groups
                    )

                if src_dest_in == "subnet":
                    # print(f"{mig_data.vlan_name} vlan/subnet matches destination: {subnet}")
                    contract = ace.to_contract(
                        acl=acl,
                        tenant=mig_data.tenant,
                        src_epg=my_mig_data.epg,
                        dst_epg=mig_data.epg,
                    )
                    ew_aces.append(ace)
                    ew_contracts.append(contract)
                if src_dest_in == "supernet":
                    subnet_str = ""
                    for i, subnet_ in enumerate(mig_data.subnet):
                        if i == 0:
                            subnet_str += subnet_
                        else:
                            subnet_str += f", {subnet_}"
                    key = f"{mig_data.vlan_name}   ({subnet_str})"
                    ew_supernets.append({key: ace})

    return ew_aces, ew_contracts, ew_supernets


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
