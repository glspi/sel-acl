"""sel_aci.cli"""
from dataclasses import dataclass
from typing import Dict, List, Optional

import typer

from sel_aci import utils
import sys
from sel_acl import objs

app = typer.Typer(
    name="sel-aci",
    add_completion=False,
    help="Cisco ACI Contract Output",
)


@app.command("create", help="Spit out JSON to create ACI Contracts")
def create(
    excel_filename: Optional[str] = typer.Option(
        None,
        "--filename",
        "-f",
        prompt="Excel Filename for List of VLAN's/ACL's/tenants: ",
        metavar="Excel Filename for List of VLAN's/ACL's/tenants",
    ),
    filter_list: Optional[str] = typer.Option(
        None,
        "--filters",
        metavar="Text file containing existing filter names"
    )
) -> None:
    """
    Spit out JSON to create ACI Contracts
    """
    filters = []
    if filter_list:
        try:
            with open(filter_list) as fin:
                for line in fin.readlines():
                    filters.append(line.strip())
        except FileNotFoundError:
            print("Filter list file not found!")

    utils.create_contracts(excel_filename, filters)


@app.command("filters", help="Retrieve new filter name list")
def get_filters(
    aci: Optional[str] = typer.Option(
        None, "--ip", "-i", prompt="ACI IP/FQDN", metavar="ACI IP/FQDN"
    ),
    username: Optional[str] = typer.Option(
        None, "--username", "-u", prompt="ACI Username", metavar="ACI Username"
    ),
    password: Optional[str] = typer.Option(
        None, "--password", "-p", prompt="ACI Password", metavar="ACI Password"
    ),
    tenant: Optional[str] = typer.Option(
        None, "--tenant", "-t", prompt="ACI Tenant", metavar="ACI Tenant"
    ),
) -> None:
    utils.get_filters(aci, username, password, tenant)


if __name__ == "__main__":
    app()
