import sys
from dataclasses import dataclass

import openpyxl
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.workbook.workbook import Workbook

# Jinja Environment
j2_env = Environment(
    loader=FileSystemLoader("sel_aci/templates"),
    lstrip_blocks=True,
    trim_blocks=True,
    undefined=StrictUndefined,
)


def load_excel(filename: str) -> openpyxl.workbook.workbook.Workbook:
    try:
        tmp = openpyxl.load_workbook(filename)  # , read_only=True)
    except InvalidFileException as error:
        print(error)
        sys.exit()

    return tmp


@dataclass()
class AciData:
    tenant: str
    action: str
    protocol: str
    src_port: str
    dst_port: str
    src_epg: str
    dst_epg: str
    src_ap: str
    dst_ap: str
    subject_description: str

    def __post_init__(self):
        self.contract_name = f"{self.src_epg}_to_{self.dst_epg}_Con"

    def filters(self):
        my_filter = AciFilter(
            protocol=self.protocol, src_port=self.src_port, dst_port=self.dst_port
        )
        # filter_name = f"{self.protocol.upper()}_"
        # if self.src_port:
        #     filter_name += f"Src_{self.src_port}_"
        # if self.dst_port:
        #     filter_name += f"Dst_{self.dst_port}_"
        # filter_name += "Fltr"

        return my_filter


@dataclass()
class AciContract:
    name: str
    filter_name: str

    def to_json(self):
        j2_contract = j2_env.get_template("empty_contract.jinja2")
        new_contract = j2_contract.render(CONTRACT_NAME=self.name)
        return new_contract


@dataclass()
class AciSubject:
    filter_name: str
    action: str
    protocol: str
    description: str

    def __post_init__(self):
        self.name = f"{self.action}_{self.filter_name}"
        self.name = self.name.replace("_Fltr", "_Subj")

    def to_json(self):
        if self.protocol == "UDP":
            j2_subject = j2_env.get_template("new_subject_udp.jinja2")
        else:
            j2_subject = j2_env.get_template("new_subject.jinja2")

        kwargs = {
            "SUBJECT_NAME": self.name,
            "SUBJECT_DESCRIPTION": self.description,
            "FILTER_NAME": self.filter_name,
            "ACTION": self.action,
        }
        new_subject = j2_subject.render(**kwargs)
        return new_subject


@dataclass()
class AciFilter:
    protocol: str
    src_port: str
    dst_port: str
    name: str = None

    def __post_init__(self):
        # Set the filter name
        self.name = f"{self.protocol}_"
        if self.src_port:
            self.name += f"Src_{self.src_port}_"
        if self.dst_port:
            self.name += f"Dst_{self.dst_port}_"
        self.name += "Fltr"

    def to_json(self):
        j2_filter = j2_env.get_template("new_filter.jinja2")

        src_port_from = "unspecified"
        src_port_to = "unspecified"
        dst_port_from = "unspecified"
        dst_port_to = "unspecified"
        if self.protocol == "IP":
            protocol = "unspecified"
        else:
            protocol = self.protocol.lower()

        if self.src_port:
            if "-" in self.src_port:
                src_port_from, src_port_to = self.src_port.split("-")
            else:
                src_port_from = src_port_to = self.src_port
        if self.dst_port:
            if "-" in self.dst_port:
                dst_port_from, dst_port_to = self.dst_port.split("-")
            else:
                dst_port_from = dst_port_to = self.dst_port

        kwargs = {
            "FILTER_NAME": self.name,
            "PROTOCOL": protocol,
            "SRC_PORT_FROM": src_port_from,
            "SRC_PORT_TO": src_port_to,
            "DST_PORT_FROM": dst_port_from,
            "DST_PORT_TO": dst_port_to,
        }
        new_filter = j2_filter.render(**kwargs)

        return new_filter


@dataclass()
class CustomWorksheet:
    def __init__(self, excel_filename):
        # Load excel and get first sheet/tab
        _ = load_excel(excel_filename)
        self.worksheet: Workbook = _.active

        # Get headers and put into dict so that sheet["headername"] = "column_letter"
        self.col_dict = {}
        for col in self.worksheet.iter_cols(1, self.worksheet.max_column):
            self.col_dict[col[0].value.upper()] = col[0].column_letter

    def get_contracts(self):
        contracts = []
        for row, _ in enumerate(self.worksheet.iter_rows(), start=1):
            if row == 1:
                continue
            subject_description = self.worksheet[
                self.col_dict["REMARK"] + str(row)
            ].value
            if not subject_description:
                subject_description = ""
            data = {
                "tenant": self.worksheet[self.col_dict["SRC_TENANT"] + str(row)].value,
                "action": self.worksheet[self.col_dict["ACTION"] + str(row)].value,
                "protocol": self.worksheet[
                    self.col_dict["PROTOCOL"] + str(row)
                ].value.upper(),
                "src_port": self.worksheet[self.col_dict["SRC_PORT"] + str(row)].value,
                "dst_port": self.worksheet[self.col_dict["DST_PORT"] + str(row)].value,
                "src_epg": self.worksheet[self.col_dict["SRC_EPG"] + str(row)].value,
                "src_ap": self.worksheet[
                    self.col_dict["SRC_APPLICATION"] + str(row)
                ].value,
                "dst_epg": self.worksheet[self.col_dict["DST_EPG"] + str(row)].value,
                "dst_ap": self.worksheet[
                    self.col_dict["DST_APPLICATION"] + str(row)
                ].value,
                "subject_description": subject_description,
            }
            aci_data = AciData(**data)

            contracts.append(aci_data)

        return contracts
