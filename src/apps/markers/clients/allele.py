"""Provide a client for getting data from the ClinGen Allele Registry."""

from pydantic import ValidationError

from apps.markers.schemas.car import HLADescriptorSchema
from base.clients import (
    EntityClient,
    EntityClientError,
    EntityClientJSONError,
    EntityClientRequestError,
)
from constants import CARConstants


class AlleleClientError(EntityClientError):
    """Define a base class for `AlleleClient` errors."""


class AlleleClientDescriptorNotFoundError(AlleleClientError):
    """Raise when the descriptor is not found."""


class AlleleClientDataError(AlleleClientError):
    """Raise when the descriptor data is not valid per our schema."""


class AlleleClientRequestError(EntityClientRequestError):
    """Raise when there is an error with the allele client's HTTP request."""


class AlleleClientJSONError(EntityClientJSONError):
    """Raise when a client can't decode JSON."""


class AlleleClient(EntityClient):
    """Get data from the ClinGen Allele Registry."""

    def __init__(
        self, descriptor: str, schema: type[HLADescriptorSchema] = HLADescriptorSchema
    ) -> None:
        """Set the base URL and other members.

        Args:
             descriptor: A string describing the allele, e.g., 'A*01:01:01:119'.
             schema: A Pydantic schema for validating the descriptor data.
        """
        super().__init__(base_url=CARConstants.API_URL)
        self.descriptor = descriptor
        self.schema = schema
        self.car_url = None
        self.car_id = None

    def _get_car_error_message(self, json_data: dict) -> str:
        """Return an error message for CAR errors."""
        error_message = f"Error getting data for {self.descriptor} from the CAR\n"
        error_message += f"    CAR error name: {json_data['errName']}\n"
        error_message += f"    CAR error message: {json_data['errMsg']}"
        return error_message

    def fetch(self) -> None:
        """Fetch data from the CAR API and populate the members.

        Raises:
            AlleleClientDescriptorNotFoundError: If the descriptor is not found.
            AlleleClientDataError: If the descriptor data is not valid.
            AlleleClientRequestError: If there is a problem with the request.
            AlleleClientJSONError: If the JSON can't be decoded.
        """
        try:
            endpoint = f"{self.base_url}/desc/{self.descriptor}"
            json_data = self.get_json(endpoint)
            if "errCode" in json_data:
                raise AlleleClientDescriptorNotFoundError(
                    self._get_car_error_message(json_data)
                )
            descriptor_data = self.schema.model_validate(**json_data)
            # As part of the validation, Pydantic checks to make sure the list of HLA
            # allele records is of length 1.
            descriptor_record = descriptor_data[0]
            self.car_url = descriptor_record.at_id  # type: ignore (Should work just fine.)
            self.car_id = descriptor_record.car_id  # type: ignore (Should work just fine.)
        except ValidationError as exc:
            error_message = f"Error validating data for {self.descriptor}: {exc}"
            raise AlleleClientDataError(error_message) from exc
        except EntityClientRequestError as exc:
            error_message = f"Error fetching data for {self.descriptor}: {exc}"
            raise AlleleClientRequestError(error_message) from exc
        except EntityClientJSONError as exc:
            error_message = f"Error decoding JSON for {self.descriptor}: {exc}"
            raise AlleleClientJSONError(error_message) from exc
