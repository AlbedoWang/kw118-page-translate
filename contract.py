from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Access(Enum):
    READ = "read"
    WRITE = "write"


class Status(Enum):
    OK = "ok"
    ADDRESS = "address_fault"
    PAGE = "page_fault"
    PROTECTION = "protection_fault"


@dataclass
class Entry(Output):
    page: Annotated[int, "Virtual page number"]
    resident: Annotated[bool, "Whether mapped"]
    frame: Annotated[int, "Physical frame, ignored if not resident"]
    writable: Annotated[bool, "Whether writes are allowed"]


@dataclass
class Request(Output):
    address: Annotated[int, "Virtual byte address"]
    access: Annotated[Access, "Read or write"]


class Tool(Enum):
    COMPUTE = "translate_addresses"
    SAVE = "save_result"


class Task(Enum):
    RUN = "page-translate"


@dataclass
class ComputeInput(Output):
    page_size: Annotated[int, "page size"]
    virtual_pages: Annotated[int, "virtual pages"]
    frames: Annotated[int, "frames"]
    entries: Annotated[list[Entry], "entries"]
    requests: Annotated[list[Request], "requests"]


@dataclass
class ComputeOutput(Output):
    statuses: Annotated[list[Status], "statuses"]
    physical: Annotated[list[int], "physical"]


@dataclass
class SaveInput(Output):
    result: Annotated[ComputeOutput, "result"]


@dataclass
class SaveOutput(Output):
    path: Annotated[str, "path"]
    result: Annotated[ComputeOutput, "result"]


TOOLS = {Tool.COMPUTE: (ComputeInput, ComputeOutput), Tool.SAVE: (SaveInput, SaveOutput)}
TASKS = {Task.RUN: (ComputeInput, SaveOutput)}
