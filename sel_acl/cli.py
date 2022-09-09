"""pan_deduper.cli"""
import asyncio
import platform
import sys
from typing import Optional

import typer

from sel_acl import utils

app = typer.Typer(
    name="sel_acl",
    add_completion=False,
    help="Cisco ACL Migration Tool",
)

# friggin windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.command("test", help="Initial tests")
def test(
    excel_filename: Optional[str] = typer.Option(
        None,
        "--filename",
        "-f",
        prompt="Excel FIlename for List of VLAN's/ACL's: ",
    ),
    vlan: Optional[int] = typer.Option(
        None, "--vlan", "-v", prompt="Vlan number to be migrated: "
    ),
    test: Optional[str] = typer.Option(
        None,
        "--test",
        "-t",
    )
) -> None:
    """
    Testing

    Args:
        excel_filename: filename.xml
        vlan: vlan number
    """
    print("\n\tLoading Time!\n")

    # try:
    #     with open(filename, encoding="utf8") as f:
    #         _ = f.read()
    # except OSError as e:
    #     print(e)
    #     print("\nFile open failed...typo?\n")
    #     sys.exit(1)

    if test == 'logic':
        utils.run_logic(excel_filename, vlan)
    else:
        utils.run(excel_filename, vlan)


if __name__ == "__main__":
    app()
