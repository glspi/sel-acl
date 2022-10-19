import sys
from typing import Any, Dict, List

import httpx


class ACI:
    """ACI API"""

    def __init__(self, aci: str, username: str, password: str) -> None:
        self.session: Dict[str, Any] = {}
        self.aci = aci
        self.username = username
        self.password = password
        self.base_url = f"https://{aci}/api/"
        self.token = ""
        self.login_data = {}

    def login(self) -> None:
        sess = httpx.Client(verify=False)
        params = {
            "aaaUser": {"attributes": {"name": self.username, "pwd": self.password}}
        }
        url = self.base_url + "aaaLogin.json"

        try:
            response = sess.post(url=url, json=params)
        except httpx.RequestError as e:
            print(f"{url=}")
            print("Request error: ", e)
            sys.exit()
        except httpx.HTTPStatusError as e:
            print(f"{url=}")
            print("HTTP Status error: ", e)
            sys.exit()

        if not response.status_code == 200:
            print("Login error, exiting..")
            print(response.json())
            sys.exit()
        else:

            try:
                self.token = response.json()["imdata"][0]["aaaLogin"]["attributes"][
                    "token"
                ]
                self.login_data = {"token": self.token}
                self.session[self.token] = sess
            except Exception:
                print("Response:")
                print(response.json())
                print("Unknown error getting token, exiting..")
                sys.exit()

    def get_filters(self, tenant: str) -> List[str]:
        url = (
            self.base_url
            + f"mo/uni/tn-{tenant}.json?query-target=children&target-subtree-class=vzFilter"
        )

        try:
            response = self.session[self.token].get(url=url)
        except httpx.RequestError as e:
            print(f"{url=}")
            print("Request error: ", e)
            sys.exit()
        except httpx.HTTPStatusError as e:
            print(f"{url=}")
            print("HTTP Status error: ", e)
            sys.exit()

        if not response.status_code == 200:
            print("Login error, exiting..")
            print(response.json())
            sys.exit()
        else:
            try:
                filters = []
                temp = response.json()["imdata"]
                for aci_filter in temp:
                    name = aci_filter["vzFilter"]["attributes"]["name"]
                    filters.append(name)
            except Exception:
                print("Response:")
                print(response.json())
                print("Unknown error getting filters, exiting..")
                sys.exit()

            return filters
