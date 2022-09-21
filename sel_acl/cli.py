"""sel_acl.cli"""
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

import typer
from rich.pretty import pprint

from sel_acl import objs, utils
from sel_acl.objs import ACL

app = typer.Typer(
    name="sel_acl",
    add_completion=False,
    help="Cisco ACL Migration Tool",
)


@dataclass
class MyParams:
    ws: objs.CustomWorksheet
    mig_data: objs.MigrationData
    addr_groups: Dict[str, Dict[str, List]]
    port_groups: Dict[str, Dict[str, List]]
    acls: List[ACL]


@app.command(
    "ns",
    help="Spit out North/South ACL's with remarks for East/West traffic added, in CIDR notation.",
)
def north_south() -> None:
    """
    north/south!
    """
    utils.run_ns(
        MyParams.acls,
        MyParams.addr_groups,
        MyParams.port_groups,
        MyParams.ws,
        MyParams.mig_data,
    )


@app.command("ew", help="Create contracts.xlsx file for review.")
def east_west():
    """
    east/west!
    :return:
    """
    utils.run_ew(
        acls=MyParams.acls,
        addr_groups=MyParams.addr_groups,
        port_groups=MyParams.port_groups,
        ws=MyParams.ws,
        mig_data=MyParams.mig_data,
    )


@app.command("cidr", help="Spit out ACL as-is in CIDR notation.")
def cidr():
    """
    east/west!
    :return:
    """
    utils.run_cidr(
        acls=MyParams.acls,
        addr_groups=MyParams.addr_groups,
        port_groups=MyParams.port_groups,
    )


def acl_compare(compare: bool):
    if compare:
        acl_filename = input("Filename containing both ACL's: ")
        acl_1 = input("ACL name (new/source): ")
        acl_2 = input("Compare with ACL name (existing): ")
        obj_filename = input("Filename containing object-groups: ")

        acl_1 = utils.get_acl_from_file(filename=acl_filename, name=acl_1)
        acl_2 = utils.get_acl_from_file(filename=acl_filename, name=acl_2)
        addr_groups = utils.get_addrgroups_from_file(filename=obj_filename)
        port_groups = utils.get_portgroups_from_file(filename=obj_filename)

        acl_1.set_cidrs_ports(addr_groups=addr_groups, port_groups=port_groups)
        acl_2.set_cidrs_ports(addr_groups=addr_groups, port_groups=port_groups)

        new_acl = utils.trim_acl(acl_1, acl_2, addr_groups, port_groups)

        print(new_acl.output_cidr(name=f"Trimmed-{acl_1.name}"))
        raise typer.Exit()


@app.callback()
def main(
    excel_filename: Optional[str] = typer.Option(
        None,
        "--filename",
        "-f",
        prompt="Excel Filename for List of VLAN's/ACL's/tenants: ",
        metavar="Excel Filename for List of VLAN's/ACL's/tenants",
    ),
    vlan: Optional[int] = typer.Option(
        None,
        "--vlan",
        "-v",
        prompt="Vlan number to be migrated: ",
        metavar="Vlan number to be migrated:",
    ),
    acls: Optional[str] = typer.Option(
        None,
        "--acls",
        "-a",
        prompt="Filename containing the ACL's: ",
        metavar="Filename containing the ACL's",
    ),
    obj_groups: Optional[str] = typer.Option(
        None,
        "--groups",
        "-g",
        prompt="Filename containing the Object Groups (IOS-XE): ",
        metavar="Filename containing the Object Groups (IOS-XE)",
    ),
    compare: Optional[bool] = typer.Option(
        None,
        "--compare",
        "-c",
        metavar="Compare 2 (ios-xe only) ACL's manually.",
        is_eager=True,
        callback=acl_compare,
    ),
) -> None:

    # Set initial data
    kwargs = utils.get_initial_data(
        excel_filename=excel_filename, vlan=vlan, obj_groups=obj_groups
    )
    for arg in kwargs:
        setattr(MyParams, arg, kwargs[arg])

    # Get Existing ACL in/out
    MyParams.acls = []
    acl_in = utils.get_acl_from_file(filename=acls, name=MyParams.mig_data.acl_name_in)
    if acl_in:
        MyParams.acls.append(acl_in)
    acl_out = utils.get_acl_from_file(
        filename=acls, name=MyParams.mig_data.acl_name_out
    )
    if acl_out:
        MyParams.acls.append(acl_out)


if __name__ == "__main__":
    app()
