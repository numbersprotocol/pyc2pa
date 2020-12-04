import sys
import json

# method to parse json
def parse_json(fname):
    with open(fname) as f:
        data = json.load(f)

    return data

# method for converting label into hexadecimal
# output in list format
def get_hex(label, indent = 0, sec_indent = -1):
    if sec_indent == -1:
        sec_indent = indent
    result = []
    for i in range(len(label)):
        if i % 16 == 0:
            if i != 0:
                indent = sec_indent
        result.append(("%02x" % (ord(label[i]))))
    return result

# method for getting label hex
def get_label_hex(label):

    label_hex = get_hex(label)
    label_hex.append('00')

    return label_hex

# calculating label size
def calc_label_size(label):

    label_hex = get_label_hex(label)
    label_size = len(label_hex)

    return label_size

# t_box is either jumb or jumd
# method for generating hex and size for t_box
def superbox_description_tbox(sub_box):

    if sub_box == "jumb":
        hex = ['6A', '75', '6D', '62']
        size = len(hex)
    if sub_box == 'jumd':
        hex = ['6A', '75', '6D', '64']
        size = len(hex)
    
    return hex, size

# type box method
def type(label):

    if label == 'assertion':
        type = ['63', '61', '61', '73', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'claim':
        type = ['63', '61', '63', '6c', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'signature':
        type = ['63', '61', '73', '67', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'store':
        type = ['63', '61', '73', '74', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'cai':
        type = ['63', '61', '63', '62', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)

    return type, size

# toggle box method
def toggle():

    type = ['03']
    size = len(type)

    return type, size

# method for setting content box (json, uuid)
def content_t_box(type):

    if type == 'json':
        hex = ['6A', '73', '6F', '6E']
        size = len(hex)
    if type == 'uuid':
        hex = ['75', '75', '69', '64']
        size = len(hex)
    
    return hex, size

# calculating l_box for content box
def content_l_box(type, data):

    tbox_size = content_t_box(type)[1]
    if type == 'json':
        payload_hex = get_hex(data)
        payload_size = len(payload_hex)
    if type == 'uuid':
        payload_hex = ['63', '61', '61', '73', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        payload_size = len(payload_hex)
    total = 4 + tbox_size + payload_size
    l_box = ['0x00', '0x00', '0x00']
    l_box.append(hex(total))

    return l_box, total

def json_content_l_box(type, fname):

    data = json.dumps(parse_json(fname))

    tbox_size = content_t_box(type)[1]
    if type == 'json':
        payload_hex = get_hex(data)
        payload_size = len(payload_hex)
    if type == 'uuid':
        payload_hex = ['63', '61', '73', '67', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        payload_size = len(payload_hex)
    total = 4 + tbox_size + payload_size
    l_box = ['00', '00', '00']
    l_box.append(hex(total))

    return l_box, total

def four_json_content_l_box(type, fname_1, fname_2, fname_3, fname_4):

    data_1 = json.dumps(parse_json(fname_1))
    data_2 = json.dumps(parse_json(fname_2))
    data_3 = json.dumps(parse_json(fname_3))
    data_4 = json.dumps(parse_json(fname_4))


    tbox_size = content_t_box(type)[1]
    
    payload_hex_1 = get_hex(data_1)
    payload_size_1 = len(payload_hex_1)

    payload_hex_2 = get_hex(data_2)
    payload_size_2 = len(payload_hex_2)

    payload_hex_3 = get_hex(data_3)
    payload_size_3 = len(payload_hex_3)

    payload_hex_4 = get_hex(data_4)
    payload_size_4 = len(payload_hex_4)
    
    total = 4 + tbox_size + payload_size_1 + payload_size_2 + payload_size_3 + payload_size_4
    l_box = ['00', '00', '00']
    l_box.append(hex(total))

    return l_box, total

# method for l_box in description box
def description_l_box(content_type, label, block):

    t_box_size = superbox_description_tbox(content_type)[1]
    type_size = type(block)[1]
    toggle_size = toggle()[1]
    label_size = calc_label_size(label)

    total = 4 + t_box_size + type_size + toggle_size + label_size

    l_box = ['00', '00', '00']
    l_box.append(hex(total))

    return l_box, total

# method for l_box in superbox
def superbox_l_box(content_type, desc_size, content_size):

    t_box_size = superbox_description_tbox(content_type)[1]
    total = 4 + t_box_size + desc_size + content_size

    l_box = ['00', '00', '00']
    l_box.append(hex(total))

    return l_box, total

# method for getting payload size for cai_store
def cai_store_payload_size(ass_size, claim_size, sign_size):

    total = ass_size + claim_size + sign_size

    return total

# method for getting payload size for cai_store
def cai_store_payload_size_four(ass_size_1, ass_size_2, ass_size_3, ass_size_4, claim_size, sign_size):

    total = ass_size_1 + ass_size_2 + ass_size_3 + ass_size_4+ claim_size + sign_size

    return total

# method for cai_store superbox l_box
def cai_store_superbox_l_box(content_type, desc_size, payload_size):

    t_box_size = superbox_description_tbox(content_type)[1]
    total = 4 + t_box_size + payload_size + desc_size

    l_box = ['00', '00', '00']
    l_box.append(hex(total))

    return l_box, total

# method for generating assertion, claim, and signature block
def create_block(super_l_box, super_t_box, desc_l_box, desc_t_box, type, toggle, label, content_l_box, cont_t_box, fname):

    data = json.dumps(parse_json(fname))

    t_box_super = superbox_description_tbox(super_t_box)
    t_box_desc = superbox_description_tbox(desc_t_box)
    t_box_content = content_t_box(cont_t_box)

    label_hex = get_label_hex(label)

    if cont_t_box == 'json':
        data_hex = get_hex(data)
    if cont_t_box == 'uuid':
        data_hex = ['63', '61', '61', '73', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']

    block = super_l_box + t_box_super[0] + desc_l_box + t_box_desc[0] + type + toggle + label_hex + content_l_box + t_box_content[0] + data_hex

    return block

def create_block_assertion(super_l_box, super_t_box, desc_l_box, desc_t_box, type, toggle, label, content_l_box, cont_t_box, ass_content):

    t_box_super = superbox_description_tbox(super_t_box)
    t_box_desc = superbox_description_tbox(desc_t_box)
    t_box_content = content_t_box(cont_t_box)

    label_hex = get_label_hex(label)

    block = super_l_box + t_box_super[0] + desc_l_box + t_box_desc[0] + type + toggle + label_hex + content_l_box + t_box_content[0] + ass_content

    return block

def create_assertion_block(super_l_box, super_t_box, desc_l_box, desc_t_box, type, toggle, label, content_l_box, cont_t_box, fname_1, fname_2, fname_3, fname_4):

    data_1 = json.dumps(parse_json(fname_1))
    data_2 = json.dumps(parse_json(fname_2))
    data_3 = json.dumps(parse_json(fname_3))
    data_4 = json.dumps(parse_json(fname_4))


    t_box_super = superbox_description_tbox(super_t_box)
    t_box_desc = superbox_description_tbox(desc_t_box)
    t_box_content = content_t_box(cont_t_box)

    label_hex = get_label_hex(label)

    data_hex_1 = get_hex(data_1)
    data_hex_2 = get_hex(data_2)
    data_hex_3 = get_hex(data_3)
    data_hex_4 = get_hex(data_4)

    block = super_l_box + t_box_super[0] + desc_l_box + t_box_desc[0] + type + toggle + label_hex + content_l_box + t_box_content[0] + data_hex_1 + data_hex_2 + data_hex_3 + data_hex_4 

    return block

# method for generating cai and store block
def create_cai_store_block(super_l_box, super_t_box, desc_l_box, desc_t_box, type, toggle, label):
    t_box_super = superbox_description_tbox(super_t_box)
    t_box_desc = superbox_description_tbox(desc_t_box)
    label_hex = get_label_hex(label)
    block = super_l_box + t_box_super[0] + desc_l_box + t_box_desc[0] + type + toggle + label_hex

    return block

# method for generating complete cai metadata injection
def create_complete(cai_l_box, cai_block, store_block, assertion_block, claim_block, signature_block):

    l_box = ['00']
    size = 10 + cai_l_box
    size_hex = hex(size)
    l_box.append(size_hex)

    header = ['FF', 'EB']
    c_box = get_hex("JP")
    box_remain = ['00', '01', '00', '00', '00','01']

    final_cai_block = header + l_box + c_box + box_remain + cai_block + store_block + assertion_block + claim_block + signature_block

    return final_cai_block

def create_complete_final(cai_l_box, cai_block, store_block, assertion_block, claim_block, signature_block,ass_block1, ass_block_2, ass_block_3, ass_block_4):

    l_box = ['00']
    size = 10 + cai_l_box
    size_hex = hex(size)
    l_box.append(size_hex)

    header = ['FF', 'EB']
    c_box = get_hex("JP")
    box_remain = ['00', '01', '00', '00', '00','01']

    final_cai_block = header + l_box + c_box + box_remain + cai_block + store_block + assertion_block + ass_block1 + ass_block_2 + ass_block_3 + ass_block_4 + claim_block + signature_block

    return final_cai_block

def create_complete_4(cai_l_box, cai_block, store_block, assertion_block_1, assertion_block_2, assertion_block_3, assertion_block_4, claim_block, signature_block):

    l_box = ['00']
    size = 10 + cai_l_box
    size_hex = hex(size)
    l_box.append(size_hex)

    header = ['FF', 'EB']
    c_box = get_hex("JP")
    box_remain = ['00', '01', '00', '00', '00','01']

    final_cai_block = header + l_box + c_box + box_remain + cai_block + store_block + assertion_block_1 + assertion_block_2 + assertion_block_3 + assertion_block_4 + claim_block + signature_block

    return final_cai_block

def create_json_injection(claim_data, assertion_data):

    # create assertion block
    ass_content = json_content_l_box('json', assertion_data)
    ass_desc = description_l_box('jumd', 'cai.assertions', 'assertion')
    ass_super = superbox_l_box('jumb', ass_desc[1], ass_content[1])
    # print ass_super
    ass_block = create_block(ass_super[0], 'jumb', ass_desc[0], 'jumd', type('assertion')[0], toggle()[0], 'cai.assertions', ass_content[0], 'json',  assertion_data)

    # create claim block
    claim_content = json_content_l_box('json', claim_data)
    claim_desc = description_l_box('jumd', 'cai.claim', 'claim')
    claim_super = superbox_l_box('jumb', claim_desc[1], claim_content[1])
    # print claim_super
    claim_block = create_block(claim_super[0], 'jumb', claim_desc[0], 'jumd', type('claim')[0], toggle()[0], 'cai.claim', claim_content[0], 'json',  claim_data)


    sig_content = json_content_l_box('uuid', assertion_data)
    sig_desc = description_l_box('jumd', 'cai.signature', 'signature')
    sig_super = superbox_l_box('jumb', sig_desc[1], sig_content[1])
    # print sig_super
    sig_block = create_block(sig_super[0], 'jumb', sig_desc[0], 'jumd', type('signature')[0], toggle()[0], 'cai.signature', sig_content[0], 'uuid', assertion_data)

    store_payload =  cai_store_payload_size(ass_super[1], claim_super[1], sig_super[1])
    store_desc = description_l_box('jumd', 'cb.starling_1', 'store')
    store_super = cai_store_superbox_l_box('jumb', store_desc[1], store_payload)
    # print store_super
    store_block = create_cai_store_block(store_super[0], 'jumb', store_desc[0], 'jumd', type('store')[0], toggle()[0], 'cb.starling_1')

    cai_payload = store_super[1]
    cai_desc = description_l_box('jumd', 'cai', 'cai')
    cai_super = cai_store_superbox_l_box('jumb', cai_desc[1], cai_payload)
    # print cai_super
    cai_block = create_cai_store_block(cai_super[0], 'jumb', cai_desc[0], 'jumd', type('cai')[0], toggle()[0], 'cai')

    return create_complete(cai_super[1], cai_block, store_block, ass_block, claim_block, sig_block)

def create_four_json_injection(claim_data, assertion_data_1, assertion_data_2, assertion_data_3, assertion_data_4, signature_data):
    
    # create assertion block (location.precise)
    ass_content_1 = json_content_l_box('json', assertion_data_1)
    ass_desc_1 = description_l_box('jumd', 'starling.location.precise', 'assertion')
    ass_super_1 = superbox_l_box('jumb', ass_desc_1[1], ass_content_1[1])
    # print ass_super
    ass_block_1 = create_block(ass_super_1[0], 'jumb', ass_desc_1[0], 'jumd', type('assertion')[0], toggle()[0], 'starling.location.precise', ass_content_1[0], 'json',  assertion_data_1)

    # create assertion block (device)
    ass_content_2 = json_content_l_box('json', assertion_data_2)
    ass_desc_2 = description_l_box('jumd', 'starling.device', 'assertion')
    ass_super_2 = superbox_l_box('jumb', ass_desc_2[1], ass_content_2[1])
    # print ass_super
    ass_block_2 = create_block(ass_super_2[0], 'jumb', ass_desc_2[0], 'jumd', type('assertion')[0], toggle()[0], 'starling.device', ass_content_2[0], 'json',  assertion_data_2)

    # create assertion block (sensor)
    ass_content_3 = json_content_l_box('json', assertion_data_3)
    ass_desc_3 = description_l_box('jumd', 'starling.sensor', 'assertion')
    ass_super_3 = superbox_l_box('jumb', ass_desc_3[1], ass_content_3[1])
    # print ass_super
    ass_block_3 = create_block(ass_super_3[0], 'jumb', ass_desc_3[0], 'jumd', type('assertion')[0], toggle()[0], 'starling.sensor', ass_content_3[0], 'json',  assertion_data_3)
    
    # create assertion block (integrity)
    ass_content_4 = json_content_l_box('json', assertion_data_4)
    ass_desc_4 = description_l_box('jumd', 'starling.integrity', 'assertion')
    ass_super_4 = superbox_l_box('jumb', ass_desc_4[1], ass_content_4[1])
    # print ass_super
    ass_block_4 = create_block(ass_super_4[0], 'jumb', ass_desc_4[0], 'jumd', type('assertion')[0], toggle()[0], 'starling.integrity', ass_content_4[0], 'json',  assertion_data_4)
    
    # create assertion block
    ass_content = ass_block_1 + ass_block_2 + ass_block_3 + ass_block_4
    ass_content_l_box = ['00', '00', '00', hex(len(ass_content))]
    ass_desc = description_l_box('jumd', 'cai.assertions', 'assertion')
    ass_super = superbox_l_box('jumb', ass_desc[1], len(ass_content))
    ass_block = create_cai_store_block(ass_super[0], 'jumb', ass_desc[0], 'jumd', type('assertion')[0], toggle()[0], 'cai.assertions')
    
    # create claim block
    claim_content = json_content_l_box('json', claim_data)
    claim_desc = description_l_box('jumd', 'starling.claim', 'claim')
    claim_super = superbox_l_box('jumb', claim_desc[1], claim_content[1])
    # print claim_super
    claim_block = create_block(claim_super[0], 'jumb', claim_desc[0], 'jumd', type('claim')[0], toggle()[0], 'starling.claim', claim_content[0], 'json',  claim_data)

    sig_content = json_content_l_box('json', signature_data)
    sig_desc = description_l_box('jumd', 'starling.signature', 'signature')
    sig_super = superbox_l_box('jumb', sig_desc[1], sig_content[1])
    # print sig_super
    sig_block = create_block(sig_super[0], 'jumb', sig_desc[0], 'jumd', type('signature')[0], toggle()[0], 'starling.signature', sig_content[0], 'json', signature_data)

    store_payload =  cai_store_payload_size(ass_super[1], claim_super[1], sig_super[1])
    store_desc = description_l_box('jumd', 'cb.starling_1', 'store')
    store_super = cai_store_superbox_l_box('jumb', store_desc[1], store_payload)
    # print store_super
    store_block = create_cai_store_block(store_super[0], 'jumb', store_desc[0], 'jumd', type('store')[0], toggle()[0], 'cb.starling_1')

    cai_payload = store_super[1]
    cai_desc = description_l_box('jumd', 'cai', 'cai')
    cai_super = cai_store_superbox_l_box('jumb', cai_desc[1], cai_payload)
    # print cai_super
    cai_block = create_cai_store_block(cai_super[0], 'jumb', cai_desc[0], 'jumd', type('cai')[0], toggle()[0], 'cai')

    return create_complete_final(cai_super[1], cai_block, store_block, ass_block, claim_block, sig_block, ass_block_1, ass_block_2, ass_block_3, ass_block_4)

def main():

    claim_data = sys.argv[1]
    assertion_data_1 = sys.argv[2]
    assertion_data_2 = sys.argv[3]
    assertion_data_3 = sys.argv[4]
    assertion_data_4 = sys.argv[5]
    sig_data = sys.argv[6]


    # print "###############################################################"
    # print "# Staring CAI-Tool                                            #"
    # print "###############################################################"

    # currently only works with specified number of assertions
    # need to change to make code more dynamic
    result = create_four_json_injection(claim_data, assertion_data_1, assertion_data_2, assertion_data_3, assertion_data_4, sig_data)
    print result
    print len(result)

if __name__ == "__main__":
    main()




