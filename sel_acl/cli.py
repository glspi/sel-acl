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
    addrgroups: str


# @app.command("test", help="Initial tests")
# def test(
#     excel_filename: Optional[str] = typer.Option(
#         None,
#         "--filename",
#         "-f",
#         prompt="Excel FIlename for List of VLAN's/ACL's: ",
#     ),
#     vlan: Optional[int] = typer.Option(
#         None, "--vlan", "-v", prompt="Vlan number to be migrated: "
#     ),
#     test: Optional[str] = typer.Option(
#         None,
#         "--test",
#         "-t",
#     )
# ) -> None:
#     """
#     Testing
#
#     Args:
#         excel_filename: filename.xml
#         vlan: vlan number
#     """
#     print("\n\tLoading Time!\n")
#
#     # try:
#     #     with open(filename, encoding="utf8") as f:
#     #         _ = f.read()
#     # except OSError as e:
#     #     print(e)
#     #     print("\nFile open failed...typo?\n")
#     #     sys.exit(1)
#
#     if test == 'logic':
#         utils.run_logic(excel_filename, vlan)
#     else:
#         utils.run(excel_filename, vlan)


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
        addrgroups=Params.addrgroups,
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
        addrgroups=Params.addrgroups,
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
        addrgroups=Params.addrgroups,
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
    addrgroups: Optional[str] = typer.Option(
        None,
        "--groups",
        "-g",
        prompt="Filename containing the Object Groups (IOS-XE): ",
    ),
) -> None:
    Params.excel_filename = excel_filename
    Params.vlan = vlan
    Params.acls = acls
    Params.addrgroups = addrgroups


if __name__ == "__main__":
    app()
