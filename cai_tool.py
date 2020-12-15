import sys
import json

# method for parsing json
def parse_json(fname):
    with open(fname) as f:
        data = json.load(f)

    output = json.dumps(data)

    return output

# method for converting label into hexadecimals
def convert_to_hex(label, indent = 0, sec_indent = -1):
    if sec_indent == -1:
        sec_indent = indent
    result = []
    for i in range(len(label)):
        if i % 16 == 0:
            if i != 0:
                indent = sec_indent
        result.append(("%2x" % (ord(label[i]))))

    return result

# format to appropriate label hex
# label hex has 00 at the end signifying \0
def format_label_hex(label):
    label_hex = convert_to_hex(label)
    label_hex.append('00')

    return label_hex

# method for calculating label_hex size 
# important for LBox Description Calculations
def calc_label_hex_size(label):

    size = len(format_label_hex(label))

    return size

# description box has type attribute
# method for setting hex for different types
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

# method for setting toggle box method
def toggle():
    type = ['03']
    size = len(type)

    return type, size

# method for formatting l_box hex
def format_hex(hex):
    
    # remove 0x
    return_hex = hex[2:]

    return return_hex

# method for generating l_box hex and size for content box
def get_content_lbox(fname):
    data = parse_json(fname)

    t_box_size = len(convert_to_hex('json'))
    
    payload_size = len(convert_to_hex(data))

    total_size = 4 + t_box_size + payload_size

    l_box = ['00', '00', '00']
    l_box.append(format_hex(hex(total_size)))

    return l_box, total_size

# method for generating l_box hex and size for description box
def get_description_l_box(label, block):
    t_box_size = len(convert_to_hex('jumd'))
    type_size = type(block)[1]
    toggle_size = toggle()[1]
    label_size = calc_label_hex_size(label)

    total_size = 4 + t_box_size + type_size + toggle_size + label_size
    l_box = ['00', '00', '00']
    l_box.append(format_hex(hex(total_size)))

    return l_box, total_size

# method for generating l_box hex and size for superbox
def get_superbox_l_box(description_size, content_size):
    t_box_size = len(convert_to_hex('jumb'))

    total_size = 4 + t_box_size + description_size + content_size
    l_box = ['00', '00', '00']
    l_box.append(format_hex(hex(total_size)))

    return l_box, total_size

# method for calculating payload size
def cai_store_payload_size(assertion, claim, signature):
    total_size = assertion + claim + signature

    return total_size

# method for cai_store l_box hex and size for superbox
def get_l_box_super_cai_store(description_size, payload_size):

    t_box_size = len(convert_to_hex('jumb'))
    total = 4 + t_box_size + description_size + payload_size

    l_box = ['00', '00', '00']
    l_box.append(format_hex(hex(total)))

    return l_box, total

# method for creating super_box (l_box & t_box)
def create_super_box(l_box):

    t_box = convert_to_hex('jumb')
    block = l_box + t_box

    return block

# method for creating description_box (l_box, t_box, type, toggle, label)
def create_description_box(l_box, type_label, label):

    t_box = convert_to_hex('jumd')
    label_hex = format_label_hex(label)
    type_box = type(type_label)[0]

    block = l_box + t_box + type_box + toggle()[0] + label_hex

    return block

# method for creating content_box (l_box, t_box, data)
def create_content_box(l_box, fname):
    data = parse_json(fname)
    data_hex = convert_to_hex(data)

    t_box = convert_to_hex('json')
    block = l_box + t_box + data_hex

    return block

# method for creating full JUMBF box (super + description + content)
def make_block(super, description, content):

    block = super + description + content

    return block

# method for create partial JUMBF blox (for cai, cai_store, assertion_store)
def make_store_block(super, desciption):

    block = super + desciption

    return block

# methof for creating block injections
def create_injection_block(cai_block, store_block, assertion_store, assertion, claim, signature, size):
    l_box = ['00']
    total_size = 10 + size
    total_size_hex = format_hex(hex(total_size))
    l_box.append(total_size_hex)

    header = ['FF', 'EB']
    c_box = convert_to_hex('JP')
    box_remain = ['00', '01', '00', '00', '00','01']

    block = header + l_box + c_box + box_remain + cai_block + store_block + assertion_store + assertion + claim + signature

    return block

def run_assertion(number_assertions):

    list = []
    label = []

    for i in range(number_assertions):
        fname = input('Assertion JSON: ')
        label_name = input('Assertion Label: ')

        list.append(fname)
        label.append(label_name)

    return list, label

def create_assertions(list, label):

    assertion_blocks = []
    super_l_box_list = []
    total = 0

    for i in list:
        for j in label:
            
            # create content l_box & content block
            content_lbox = get_content_lbox(i)
            content_lbox_block = create_content_box(content_lbox[0], i)
            
            # create description 1_box & description block
            description_lbox = get_description_l_box(j, 'assertion')
            description_block = create_description_box(description_lbox[0], 'assertion', j)

            # create superbox 1_box and superbox block
            superbox_lbox = get_superbox_l_box(description_lbox[1], content_lbox[1])
            superbox_block = create_super_box(superbox_lbox[0])

            # create complete assertion box
            block = make_block(superbox_block, description_block, content_lbox_block)
        assertion_blocks.append(block)
        super_l_box_list.append(superbox_lbox[1])

    for i in super_l_box_list:
        total = total + i

    return assertion_blocks, total

def run_claim():
    
    fname = input("Claim JSON: ")

    return fname

def create_claim(fname):
    # create content l_box & content block
    content_lbox = get_content_lbox(fname)
    content_lbox_block = create_content_box(content_lbox[0], fname)
            
    # create description 1_box & description block
    description_lbox = get_description_l_box('cai.claim', 'claim')
    description_block = create_description_box(description_lbox[0], 'claim', 'cai.claim')

    # create superbox 1_box and superbox block
    superbox_lbox = get_superbox_l_box(description_lbox[1], content_lbox[1])
    superbox_block = create_super_box(superbox_lbox[0])

    # create complete assertion box
    block = make_block(superbox_block, description_block, content_lbox_block)

    return block, superbox_lbox[1]

def run_signature():
    
    fname = input("Signature JSON: ")

    return fname

def create_signature(fname):
    # create content l_box & content block
    content_lbox = get_content_lbox(fname)
    content_lbox_block = create_content_box(content_lbox[0], fname)
            
    # create description 1_box & description block
    description_lbox = get_description_l_box('cai.signature', 'signature')
    description_block = create_description_box(description_lbox[0], 'signature', 'cai.signature')

    # create superbox 1_box and superbox block
    superbox_lbox = get_superbox_l_box(description_lbox[1], content_lbox[1])
    superbox_block = create_super_box(superbox_lbox[0])

    # create complete assertion box
    block = make_block(superbox_block, description_block, content_lbox_block)

    return block, superbox_lbox[1]

def run_store():
    label = input("Store label: ")

    return label

def create_complete(cai_l_box, cai_block, store_block, assertion_block, assertions, claim_block, signature_block):

    l_box = ['00']
    size = 10 + cai_l_box
    size_hex = format_hex(hex(size))
    l_box.append(size_hex)

    header = ['FF', 'EB']
    c_box = convert_to_hex('JP')
    box_remain = ['00', '01', '00', '00', '00','01']

    final_cai_block = header + l_box + c_box + box_remain + cai_block + store_block + assertion_block + assertions + claim_block + signature_block

    return final_cai_block

def process():
    number_assertions = input('How many assertions? ')
    number_assertions = int(number_assertions)

    if number_assertions > 0:
        fname_list = run_assertion(number_assertions)

        ass = create_assertions(fname_list[0], fname_list[1])

        assertions = []
        for i in ass[0]:
            assertions = assertions + i

        claim_fname = run_claim()

        claim = create_claim(claim_fname)

        sign_fname = run_signature()

        signature = create_signature(sign_fname)

        # create assertion block
        ass_desc = get_description_l_box('cai.assertions', 'assertion')
        ass_desc_block = create_description_box(ass_desc[0], 'assertion', 'cai.assertions')
        ass_super = get_superbox_l_box(ass_desc[1], ass[1])
        ass_super_block = create_super_box(ass_super[0])

        ass_block = make_store_block(ass_super_block, ass_desc_block)

        payload_size = cai_store_payload_size(ass[1], claim[1], signature[1])

        label = run_store()
        store_desc = get_description_l_box(label, 'store')
        store_desc_block = create_description_box(store_desc[0], 'store', label)
        store_super = get_l_box_super_cai_store(store_desc[1], payload_size)
        store_super_block = create_super_box(store_super[0])
        store_block = make_store_block(store_super_block, store_desc_block)

        cai_payload = store_super[1]
        cai_desc = get_description_l_box('cai', 'cai')
        cai_desc_block = create_description_box(cai_desc[0], 'cai', 'cai')
        cai_super = get_l_box_super_cai_store(cai_desc[1], cai_payload)
        cai_super_block = create_super_box(cai_super[0])
        cai_block = make_store_block(cai_super_block, cai_desc_block)

        injection = create_complete(cai_super[1], cai_block, store_block, ass_block, assertions, claim[0], signature[0])
        print(injection)

    else:
        print("Not a valid number of assertions")

    

def main():
    script = sys.argv[0]
    process()
    

if __name__ == "__main__":
    main()   
