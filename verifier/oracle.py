from contract import ComputeOutput, Status


def input_problem(v):
    if min(v.page_size, v.virtual_pages, v.frames) <= 0:
        return "dimensions must be positive"
    pages = [e.page for e in v.entries]
    if len(set(pages)) != len(pages):
        return "duplicate virtual page"
    for e in v.entries:
        if not 0 <= e.page < v.virtual_pages or (e.resident and not 0 <= e.frame < v.frames):
            return "page or resident frame out of range"
    return None


def expected(v):
    statuses, physical = [], []
    for r in v.requests:
        status, address = Status.PAGE, -1
        if r.address < 0 or r.address >= v.virtual_pages * v.page_size:
            status = Status.ADDRESS
        else:
            for e in v.entries:
                if e.page == r.address // v.page_size and e.resident:
                    status = Status.PROTECTION if r.access.value == "write" and not e.writable else Status.OK
                    if status == Status.OK:
                        address = e.frame * v.page_size + r.address % v.page_size
        statuses.append(status)
        physical.append(address)
    return ComputeOutput(statuses, physical)
