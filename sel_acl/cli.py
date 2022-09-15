"""sel_acl.cli"""
import sys
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
    addr_groups: str


@app.command("ns")
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
        addr_groups=Params.addr_groups,
        nsew="ns",
    )


@app.command("ew")
def east_west():
    """
    east/west!
    :return:
    """
    utils.run_main(
        excel_filename=Params.excel_filename,
        vlan=Params.vlan,
        acls=Params.acls,
        addr_groups=Params.addr_groups,
        nsew="ew",
    )


@app.command("cidr")
def cidr():
    """
    east/west!
    :return:
    """
    utils.run_main(
        excel_filename=Params.excel_filename,
        vlan=Params.vlan,
        acls=Params.acls,
        addr_groups=Params.addr_groups,
        nsew="cidr",
    )


@app.callback()
def main(
    excel_filename: Optional[str] = typer.Option(
        None,
        "--filename",
        "-f",
        prompt="Excel Filename for List of VLAN's/ACL's/tenants: ",
        is_eager=True,
    ),
    vlan: Optional[int] = typer.Option(
        None, "--vlan", "-v", prompt="Vlan number to be migrated: "
    ),
    acls: Optional[str] = typer.Option(
        None, "--acls", "-a", prompt="Filename containing the ACL's: "
    ),
    addr_groups: Optional[str] = typer.Option(
        None,
        "--groups",
        "-g",
        prompt="Filename containing the Object Groups (IOS-XE): ",
    ),
) -> None:
    Params.excel_filename = excel_filename
    Params.vlan = vlan
    Params.acls = acls
    Params.addr_groups = addr_groups


if __name__ == "__main__":
    app()
