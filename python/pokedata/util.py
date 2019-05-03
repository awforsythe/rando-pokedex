import struct


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def get_default_format_char(size):
    try:
        return {1: 'B', 2: 'H', 4: 'I'}[size]
    except KeyError:
        return None


def unpack(data_format, data):
    unpacked = {}

    for fmt in data_format:
        offset, size, name = fmt[0], fmt[1], fmt[2]
        if len(fmt) > 3:
            fmt_char = fmt[3] if isinstance(fmt[3], str) else None
            parse_func = fmt[3] if fmt_char is None else None
        else:
            fmt_char = get_default_format_char(size)
            parse_func = None

        value = data[offset:offset + size]
        if fmt_char:
            value = struct.unpack(fmt_char, value)[0]
        if parse_func:
            old_value = value
            value = parse_func(value)

        unpacked[name] = value

    return unpacked
