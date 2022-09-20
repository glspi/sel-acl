"""sel_acl.cli"""
from dataclasses import dataclass
from typing import Optional

import typer

from sel_acl import utils

app = typer.Typer(
    name="sel_acl",
    add_completion=False,
    help="Cisco ACL Migration Tool",
)


@dataclass
class Params:
    excel_filename: str
    vlan: int
    acls: str
    obj_groups: str


@app.command(
    "ns",
    help="Spit out North/South ACL's with remarks for East/West traffic added, in CIDR notation.",
)
def north_south(
    # northsouth: Optional[bool] = typer.Option(
    #     None,
    #     "--northsouth",
    #     "-ns"
    # ),
    # eastwest: Optional[bool] = typer.Option(
    #     None,
    #     "--eastwestw",
    #     "-ew",
    # ),
) -> None:
    """
    north/south!
    """
    utils.run_main(
        excel_filename=Params.excel_filename,
        vlan=Params.vlan,
        acls=Params.acls,
        obj_groups=Params.obj_groups,
        nsew="ns",
    )


@app.command("ew", help="Create contracts.xlsx file for review.")
def east_west():
    """
    east/west!
    :return:
    """
    utils.run_main(
        excel_filename=Params.excel_filename,
        vlan=Params.vlan,
        acls=Params.acls,
        obj_groups=Params.obj_groups,
        nsew="ew",
    )


@app.command("cidr", help="Spit out ACL as-is in CIDR notation.")
def cidr():
    """
    east/west!
    :return:
    """
    utils.run_main(
        excel_filename=Params.excel_filename,
        vlan=Params.vlan,
        acls=Params.acls,
        obj_groups=Params.obj_groups,
        nsew="cidr",
    )


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
) -> None:
    Params.excel_filename = excel_filename
    Params.vlan = vlan
    Params.acls = acls
    Params.obj_groups = obj_groups


if __name__ == "__main__":
    app()
