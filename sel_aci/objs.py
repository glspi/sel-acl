import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.workbook.workbook import Workbook
import sys
from dataclasses import dataclass


def load_excel(filename: str) -> openpyxl.workbook.workbook.Workbook:
    try:
        tmp = openpyxl.load_workbook(filename)  # , read_only=True)
    except InvalidFileException as error:
        print(error)
        sys.exit()

    return tmp


@dataclass
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


@dataclass
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
            data = {
                "tenant": self.worksheet[self.col_dict["SRC_TENANT"] + str(row)].value,
                "action": self.worksheet[self.col_dict["ACTION"] + str(row)].value,
                "protocol": self.worksheet[self.col_dict["PROTOCOL"] + str(row)].value,
                "src_port": self.worksheet[self.col_dict["SRC_PORT"] + str(row)].value,
                "dst_port": self.worksheet[self.col_dict["DST_PORT"] + str(row)].value,
                "src_epg": self.worksheet[self.col_dict["SRC_EPG"] + str(row)].value,
                "src_ap": self.worksheet[self.col_dict["SRC_APPLICATION"] + str(row)].value,
                "dst_epg": self.worksheet[self.col_dict["DST_EPG"] + str(row)].value,
                "dst_ap": self.worksheet[self.col_dict["DST_APPLICATION"] + str(row)].value,
            }
            aci_data = AciData(**data)

            contracts.append()

        return contracts
