"""sel_aci.cli"""
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

import typer

from sel_aci import objs, utils

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
    filter_file: Optional[str] = typer.Option(
        None,
        "--filters",
        "-t",
        metavar="Optional: Text file containing existing filter names",
    ),
    contract_file: Optional[str] = typer.Option(
        None,
        "--contracts",
        "-c",
        metavar="Optional: Text file containing existing contract names",
    ),
    version: Optional[str] = typer.Option(
        "4.2", "--version", "-v", metavar="Optional: Set to '5.2' for ACI 5.2 output."
    ),
) -> None:
    """
    Spit out JSON to create ACI Contracts
    """
    filter_names = []
    if filter_file:
        try:
            with open(filter_file) as fin:
                for line in fin.readlines():
                    filter_names.append(line.strip())
        except FileNotFoundError:
            print("Filter list file not found!")

    contract_names = []
    if contract_file:
        try:
            with open(contract_file) as fin:
                for line in fin.readlines():
                    contract_names.append(line.strip())
        except FileNotFoundError:
            print("Filter list file not found!")

    utils.main(excel_filename, filter_names, contract_names, version)


@app.command("get", help="Create Filter and Contract name text files.")
def get_aci_objects(
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
    utils.get_aci_objects(aci, username, password, tenant)


if __name__ == "__main__":
    app()
