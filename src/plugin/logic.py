from contract import ComputeOutput, Status


def compute(v, workspace):
    if min(v.page_size, v.virtual_pages, v.frames) <= 0 or len({e.page for e in v.entries}) != len(v.entries):
        raise ValueError("invalid dimensions or duplicate page")
    if any(e.page < 0 or e.page >= v.virtual_pages or (e.resident and not 0 <= e.frame < v.frames) for e in v.entries):
        raise ValueError("invalid page table")
    table = {e.page: e for e in v.entries}
    statuses, physical = [], []
    for r in v.requests:
        page, offset = divmod(r.address, v.page_size)
        e = table.get(page)
        if not 0 <= r.address < v.page_size * v.virtual_pages:
            status, address = Status.ADDRESS, -1
        elif e is None or not e.resident:
            status, address = Status.PAGE, -1
        elif r.access.value == "write" and not e.writable:
            status, address = Status.PROTECTION, -1
        else:
            status, address = Status.OK, e.frame * v.page_size + offset
        statuses.append(status)
        physical.append(address)
    return ComputeOutput(statuses, physical)
