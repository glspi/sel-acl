import sys
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from sel_acl.objs import ACE, ACE2, ACL, MigrationData
import re

from ciscoconfparse import CiscoConfParse
import textfsm
from rich.pretty import pprint


# ACL_FSM = open("acl.textfsm")
ACL_FSM = open("acl.textfsm")
RE_TABLE = textfsm.TextFSM(ACL_FSM)


def get_file(filename: str) -> openpyxl.workbook.workbook.Workbook:
    try:
        tmp = openpyxl.load_workbook(filename)#, read_only=True)
    except InvalidFileException as error:
        print(error)
        sys.exit()

    return tmp


def format_fsm_output(re_table, fsm_results):
    """
    FORMAT FSM OUTPUT(LIST OF LIST) INTO PYTHON LIST OF DICTIONARY VALUES BASED ON TEXTFSM TEMPLATE
    :param re_table: re_table from generic fsm search
    :param fsm_results: fsm results from generic fsm search
    :return result: updated list of dictionary values
    """
    result = []
    for item in fsm_results:
        tempdevice = {}
        for position, header in enumerate(re_table.header):
            tempdevice[header.lower()] = item[position]
        result.append(tempdevice)

    return result


def get_migration_data_from_vlan(filename: str, vlan: int):
    tmp = get_file(filename)
    sheet = tmp.active
    print(type(tmp))
    print(sheet["C9"].value)
    print('h')
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
        "subnet": sheet[col_dict["IP-ADDRESS"] + str(my_row)].value
    }
    return MigrationData(**data)


def create_new_ace(ace: ACE):
    new_ace = ""
    if not ace.remark:
        pass
    else:
        new_ace += f"remark {ace.remark}"

    return new_ace


def get_acl(name: str, acl_parser: CiscoConfParse):
    # GET ACL IN
    search_for = fr"ip access-list extended {name}"

    aces = []
    for acl in acl_parser.find_objects(search_for):
        for child in acl.children:
            re_table = textfsm.TextFSM(ACL_FSM)
            print(child.text)
            fsm_results = re_table.ParseText(child.text)
            results = format_fsm_output(re_table, fsm_results)
            if not results:
                print("ERROR WITH ABOVE LINE)")
            else:
                ace = ACE(**results[0])
                aces.append(ace)
            #pprint(results)

    return ACL(name, aces)


def get_acl2(name: str, acl_parser: CiscoConfParse):
    re_pattern = r"""
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

    rec = re.compile(re_pattern, re.X)

    search_for = fr"ip access-list extended {name}"

    aces = []
    for acl in acl_parser.find_objects(search_for):
        for child in acl.children:
            results = rec.search(child.text)
            if not results:
                print(child.text)
                print("ERROR WITH ABOVE LINE)")
            else:
                ace = ACE2(**results.groupdict())
                aces.append(ace)
            # pprint(results)

    return ACL(name, aces)


def get_existing_acls(filename: str, mig_data: MigrationData):
    with open(filename, "r") as fin:
        acl_str = fin.read()
    acl_parser = CiscoConfParse(filename)

    acl_in = get_acl(name=mig_data.acl_name_in, acl_parser=acl_parser)

    for ace in acl_in.aces:
        if ace.remark:
            new_ace = create_new_ace(ace)
            print(new_ace)

    sys.exit()


def run(filename: str, vlan: int):
    """
    Run
    :param filename:
    :param vlan:
    """

    # Get ACL/Name/Subnet/Etc from Vlan Number
    mig_data = get_migration_data_from_vlan(filename=filename, vlan=vlan)

    print(mig_data)

    acl_filename = "mytest.ios"
    my_acl = get_existing_acls(filename=acl_filename, mig_data=mig_data)



