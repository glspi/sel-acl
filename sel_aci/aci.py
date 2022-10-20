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

    def get_object_names(self, tenant: str, obj_type) -> List[str]:
        url = (
            self.base_url
            + f"mo/uni/tn-{tenant}.json?query-target=children&target-subtree-class="
        )

        if obj_type == "filters":
            url += "vzFilter"
            vzType = "vzFilter"
        elif obj_type == "contracts":
            url += "vzBrCP"
            vzType = "vzBrCP"
        else:
            print(f"Unsupported object type: {obj_type}")
            sys.exit()

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
                objs = []
                temp = response.json()["imdata"]
                for obj in temp:
                    name = obj[vzType]["attributes"]["name"]
                    objs.append(name)
            except Exception:
                print("Response:")
                print(response.json())
                print(f"Unknown error getting {obj_type}, exiting..")
                sys.exit()

            return objs
