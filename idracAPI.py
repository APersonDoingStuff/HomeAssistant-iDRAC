"""Api interface for iDEAR Redfish."""

import contextlib
import json
import subprocess

import requests
import requests.exceptions
import urllib3
from urllib3 import exceptions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class idracClient:
    """A wrapper for the idrac client."""

    connectionEstablished: bool
    powerState: str = "Off"

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
    ) -> None:
        """Initialize the idrac."""

        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self.connectionEstablished = False

    def _ping(self):
        ping_process = subprocess.Popen(
            ["ping", "-c", "5", self._host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = ping_process.communicate()

        # Check if ping was successful
        if ping_process.returncode == 0:
            # Parse output to count successful pings
            successful_count = output.decode().count("time=")
            return successful_count
        else:
            return 0  # If ping was unsuccessful, return 0

    def build_client(self) -> None:
        """Construct the idrac client."""

        getPing = self._ping()

        if getPing > 0:
            self.connectionEstablished = True
            self.powerState = self.getPowerState()

        else:
            self.connectionEstablished = False
            self.powerState = "Unknown"

    def TurnOnSystem(self):
        """Turn on the system base on idrac with redfish api."""

        if self.connectionEstablished:
            try:
                url = f"https://{self._host}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
                payload = {
                    "ResetType": "On",
                }
                headers = {"content-type": "application/json"}
                response = requests.post(
                    url,
                    data=json.dumps(payload),
                    headers=headers,
                    verify=False,
                    auth=(self._user, self._password),
                    timeout=60,
                )
            except (
                exceptions.ConnectionError,
                exceptions.HTTPError,
                exceptions.MaxRetryError,
                exceptions.NewConnectionError,
                exceptions.ResponseError,
                exceptions.TimeoutError,
                OSError,
            ):
                self.powerState = "Unknown"
                return False
            if response.status_code == 204:
                self.powerState = "On"
                return True
        self.powerState = "Unknown"
        return False

    def TurnOffSystem(self):
        """Turn on the system base off idrac with redfish api."""
        if self.connectionEstablished:
            try:
                url = f"https://{self._host}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
                payload = {
                    "ResetType": "GracefulShutdown",
                }
                headers = {"content-type": "application/json"}
                response = requests.post(
                    url,
                    data=json.dumps(payload),
                    headers=headers,
                    verify=False,
                    auth=(self._user, self._password),
                    timeout=60,
                )
            except (
                exceptions.ConnectionError,
                exceptions.HTTPError,
                exceptions.MaxRetryError,
                exceptions.NewConnectionError,
                exceptions.ResponseError,
                exceptions.TimeoutError,
                OSError,
            ):
                self.powerState = "Unknown"
                return False
            if response.status_code == 204:
                self.powerState = "Off"
                return True
        self.powerState = "Unknown"
        return False

    def getPowerState(self):
        """Get powerState from idrac with redfish api."""
        if self.connectionEstablished:
            url = f"https://{self._host}/redfish/v1/Systems/System.Embedded.1"
            headers = {"content-type": "application/json"}
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    verify=False,
                    auth=(self._user, self._password),
                    timeout=60,
                )

            except (
                exceptions.ConnectionError,
                exceptions.HTTPError,
                exceptions.MaxRetryError,
                exceptions.NewConnectionError,
                exceptions.ResponseError,
                exceptions.TimeoutError,
                OSError,
            ):
                self.connectionEstablished = False
                self.powerState = "Unknown"
                return "Unknown"

            if response.status_code == 200:
                response_output = response.__dict__
                str1 = str(response_output["_content"]).replace("\\n'", "")[2:]

                def find_values(key, json_repr):
                    results = []

                    def _decode_dict(a_dict):
                        with contextlib.suppress(KeyError):
                            results.append(a_dict[key])
                        return a_dict

                    json.loads(json_repr, object_hook=_decode_dict)

                    return results

                result = find_values("PowerState", str1)

                if len(result) == 0:
                    self.powerState = "Unknown"
                    return "Unknown"
                else:
                    self.powerState = result[0]
                    return result[0]
            else:
                return "Unknown"
        else:
            self.build_client()
        return "Unknown"
