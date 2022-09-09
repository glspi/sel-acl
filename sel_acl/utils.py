import sys

import openpyxl
from ciscoconfparse import CiscoConfParse
from openpyxl.utils.exceptions import InvalidFileException
from rich.pretty import pprint

from sel_acl.objs import ACL, MigrationData


def load_excel(filename: str) -> openpyxl.workbook.workbook.Workbook:
    try:
        tmp = openpyxl.load_workbook(filename)  # , read_only=True)
    except InvalidFileException as error:
        print(error)
        sys.exit()

    return tmp


def get_migration_data_from_vlan(filename: str, vlan: int):
    print("random excel fun:")
    tmp = load_excel(filename)
    sheet = tmp.active
    print(type(tmp))
    print(sheet["C9"].value)
    print("h")
    print(sheet.max_row, sheet.max_column)

    # Get headers
    headers = [c.value.upper() for c in next(sheet.iter_rows(min_row=1, max_row=1))]

    col_dict = {}
    for col in sheet.iter_cols(1, sheet.max_column):
        col_dict[col[0].value.upper()] = col[0].column_letter

    # Get Row for vlan
    my_row = False
    for row in sheet[col_dict["VLAN"]]:
        if row.value == vlan:
            my_row = row.row
    if not my_row:
        print("Invalid vlan? Not found..")
        sys.exit()

    data = {
        "vlan_name": sheet[col_dict["NAME"] + str(my_row)].value,
        "acl_name_in": sheet[col_dict["ACCESS-LIST-IN"] + str(my_row)].value,
        "acl_name_out": sheet[col_dict["ACCESS-LIST-OUT"] + str(my_row)].value,
        "tenant": sheet[col_dict["TENANT"] + str(my_row)].value,
        "subnet": sheet[col_dict["IP-ADDRESS"] + str(my_row)].value,
    }
    return MigrationData(**data)


def get_acl_from_file(filename: str, name: str):
    acl_parser = CiscoConfParse(filename)
    search_for = rf"ip access-list extended {name}"

    try:
        my_acl = ACL(name=name, acl=acl_parser.find_objects(search_for)[0])
    except IndexError:
        print(f"Error loading acl: '{name}' from {filename}, not found?")
        sys.exit()

    return my_acl


def run(excel_filename: str, vlan: int):
    """
    Run
    :param excel_filename:
    :param vlan:
    """

    # Get ACL/Name/Subnet/Etc from Vlan Number
    mig_data = get_migration_data_from_vlan(filename=excel_filename, vlan=vlan)

    pprint(mig_data)

    acl_filename = "mytest.ios"
    acl_in = get_acl_from_file(filename=acl_filename, name=mig_data.acl_name_in)
    acl_out = get_acl_from_file(filename=acl_filename, name=mig_data.acl_name_out)

    # for ace in acl_in.aces:
    #     if ace.remark:
    #         print(ace.nexus_output())
    #     # for ace2 in acl_out.aces:
    #     #     if ace == ace2:
    #     #         print("we found a match?!")
    #     #         pprint(ace)
    #     #         pprint(ace2)
    #     #         if "deny" in ace:
    #     #             print("uhh no way")
    #     if ace in acl_out:
    #         print("WHAAAAT")
    #         print(ace)
    #
    # for ace in acl_out.aces:
    #     if ace.remark:
    #         print(ace.remark)
    #
    # new_acl_in = acl_in.output_cidr(name="Nexus_Acl-In")
    # new_acl_out = acl_out.output_cidr(name="Nexus_Acl-Out")
    # print(new_acl_in)
    # print(new_acl_out)
    #pprint(acl_in)

    print("North South...")
    print("--------------")


def get_subnets_from_file(filename: str, exclude: str):
    tmp = load_excel(filename)
    sheet = tmp.active
    # Get headers
    headers = [c.value.upper() for c in next(sheet.iter_rows(min_row=1, max_row=1))]
    # or
    col_dict = {}
    for col in sheet.iter_cols(1, sheet.max_column):
        col_dict[col[0].value.upper()] = col[0].column_letter

    # Get Subnets
    subnets = []
    for i, row in enumerate(sheet[col_dict["IP-ADDRESS"]]):
        if i == 0:
            continue
        subnet = row.value.strip() if row.value else None
        if subnet == exclude or None:
            continue
        subnets.append(subnet)
    return subnets


def get_rows(excel_filename, column, exclude: str = ""):
    tmp = load_excel(excel_filename)
    sheet = tmp.active
    col_dict = {}
    for col in sheet.iter_cols(1, sheet.max_column):
        col_dict[col[0].value.upper()] = col[0].column_letter
    # Get Rows
    rows = []
    for i, row in enumerate(sheet[col_dict[column]]):
        if i == 0:
            continue
        value = row.value.strip() if row.value else None
        if not value:
            continue
        if value == exclude:
            continue
        rows.append(value)
    return rows


def check_destination_match(acl, excel_filename, exclude):
    all_subnets = get_subnets_from_file(filename=excel_filename, exclude=exclude)
    all_acl_names = get_rows(excel_filename=excel_filename, column="ACCESS-LIST-IN")
    print(all_acl_names)

    acl_filename = "mytest.ios"
    all_acls = [get_acl_from_file(filename=acl_filename, name=name) for name in all_acl_names]
    pprint(all_acls)
    return 'hi'


def run_logic(excel_filename: str, vlan: int):
    # Get ACL/Name/Subnet/Etc from Vlan Number
    mig_data = get_migration_data_from_vlan(filename=excel_filename, vlan=vlan)
    pprint(mig_data)

    acl_filename = "mytest.ios"
    acl_in = get_acl_from_file(filename=acl_filename, name=mig_data.acl_name_in)
    acl_out = get_acl_from_file(filename=acl_filename, name=mig_data.acl_name_out)

    __in = check_destination_match(acl_in, excel_filename, exclude=mig_data.subnet)

    # Check destination


