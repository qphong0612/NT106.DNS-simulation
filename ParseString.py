from Message import Message
from MessageQuestion import MessageQuestion
from MessageHeader import MessageHeader
from ResourceRecord import ResourceRecord
from Cache import Cache
from CacheSystem import CacheSystem


def parse_string_flag(flags: str) -> dict:
    """Parse a hex string of flags to a dictionary of flags with values converted properly."""
    # convert hex string to bin string
    bin_str = bin(int(flags, 16))[2:].rjust(16, "0")

    d_flags = dict()
    cur_bit_pos = 0

    # get 1-bit QR
    d_flags['qr'] = int(bin_str[cur_bit_pos])
    cur_bit_pos += 1

    # get 4-bit OPCODE
    d_flags['opcode'] = int(bin_str[cur_bit_pos: cur_bit_pos + 4], 2)
    cur_bit_pos += 4

    # get 1-bit AA
    d_flags['aa'] = bool(bin_str[cur_bit_pos])
    cur_bit_pos += 1

    # get 1-bit TC
    d_flags['tc'] = bool(bin_str[cur_bit_pos])
    cur_bit_pos += 1

    # get 1-bit RD
    d_flags['rd'] = bool(bin_str[cur_bit_pos])
    cur_bit_pos += 1

    # get 1-bit RA
    d_flags['ra'] = bool(bin_str[cur_bit_pos])
    cur_bit_pos += 1

    # get 3-bit Z
    z_flg = bin_str[cur_bit_pos:cur_bit_pos + 3]
    d_flags['z'] = int(z_flg)
    cur_bit_pos += 3

    # get 4-bit RCODE
    r_code = bin_str[cur_bit_pos:cur_bit_pos + 4]
    if r_code != '':
        d_flags['rcode'] = int(bin_str[cur_bit_pos: cur_bit_pos + 4], 2)
    else:
        d_flags['rcode'] = 0

    return d_flags


def parse_string_question(question: str) -> MessageQuestion:
    """Parse a question string to a MessageQuestion object."""
    fields = question.split(';')
    qname = fields[0]

    try:
        qtype = int(fields[1])
    except ValueError:
        qtype = MessageQuestion.QTYPE[fields[1]]

    try:
        qclass = int(fields[2])
    except ValueError:
        qclass = MessageQuestion.QCLASS[fields[2]]

    return MessageQuestion(qname, qtype, qclass)


def parse_string_resource_record(rr: str) -> ResourceRecord:
    """Parse a resource record string to a ResourceRecord object."""
    fields = rr.split(';')
    _name = fields[0]
    _type = int(fields[1])
    _class = int(fields[2])
    _ttl = int(fields[3])
    _rdata = fields[4]
    return ResourceRecord(_name, _type, _class, _ttl, _rdata)


def parse_string_msg(msg: str) -> Message:
    """Parse a message string to a Message object."""
    lines = msg.splitlines()

    # [header]
    header_id = lines[0]
    header_flags = lines[1]
    header_qdcount = int(lines[2])
    header_ancount = int(lines[3])
    header_nscount = int(lines[4])
    header_arcount = int(lines[5])

    # parse flags
    flags = parse_string_flag(header_flags)

    # create a MessageHeader object
    header = MessageHeader(id=int(header_id),
                           qr=flags['qr'],
                           opcode=flags['opcode'],
                           aa=flags['aa'],
                           tc=flags['tc'],
                           rd=flags['rd'],
                           ra=flags['ra'],
                           rcode=flags['rcode'])

    # [body]
    # question
    question_str = lines[6]
    question = parse_string_question(question_str)

    # tracker
    cur_line = 7

    # Create the Message object
    message = Message(header=header, question=question)

    # [KNOWN ERROR]
    # If the message is truncated, the counts will decline automatically
    # (via the _set_header_flags_automatically() method in Message class)

    # answers
    for _ in range(header_ancount):
        message.add_a_new_record_to_answer_section(parse_string_resource_record(lines[cur_line]))
        cur_line += 1

    # authority
    for _ in range(header_nscount):
        message.add_a_new_record_to_authority_section(parse_string_resource_record(lines[cur_line]))
        cur_line += 1

    # additional
    for _ in range(header_arcount):
        message.add_a_new_record_to_additional_section(parse_string_resource_record(lines[cur_line]))
        cur_line += 1

    return message


def parse_string_cache(cachestr: str) -> Cache:
    """Parse a cache string to a Cache object."""
    fields = cachestr.split('/')
    rr = parse_string_resource_record(fields[0])
    ttd = int(fields[1])
    cache = Cache(rr)
    cache._ttd = ttd
    return cache


def parse_string_cachesystem(cachesys: str) -> CacheSystem:
    """Parse a CacheSystem string to a CacheSystem object."""
    lines = cachesys.splitlines()
    sys = CacheSystem()
    sys._refresh_time = int(lines[0])
    sys._next_refresh_time = int(lines[1])
    for i in range(2, len(lines)):
        cache = parse_string_cache(lines[i])
        sys._database.append(cache)
    return sys
