#***************************************************************************
def is_empty(stack):
    return len(stack) == 0

def last(stack):
    return stack[-1]

def pop(stack):
    if not is_empty(stack):
        return stack.pop()
    else:
        BaseException("Error")

def push(stack, op):
    stack.append(op)

#***************************************************************************
def replace_reserved_words(r: str):
    r = r.replace('(', 'Þ')
    r = r.replace(')', 'δ')
    r = r.replace('{', 'ζ')
    r = r.replace('}', 'η')
    r = r.replace('[', 'θ')
    r = r.replace(']', 'ω')
    r = r.replace('|', '¶')
    r = r.replace('+', 'µ')
    r = r.replace('-', 'ß')
    return r
    
def return_reserved_words(r: str):
    r = r.replace('Þ', '(')
    r = r.replace('δ', ')')
    r = r.replace('ζ', '{')
    r = r.replace('η', '}')
    r = r.replace('θ', '[')
    r = r.replace('ω', ']')
    r = r.replace('¶', '|')
    r = r.replace('µ', '+') #unicode U+0398    
    r = r.replace('ß', '-') #unicode U+03A3
    return r

def process_string(s: str):
    result = []
    in_quotes = False
    start_idx = 0
    for i, char in enumerate(s):
        if char == '"':
            if in_quotes:
                # End of quoted substring; apply replace_reserved_words
                result.append(replace_reserved_words(s[start_idx:i]))
                in_quotes = False
            else:
                # Copy unprocessed substring and start of quoted substring
                result.append(s[start_idx:i])
                in_quotes = True
            start_idx = i + 1
    # Append remaining unprocessed substring
    result.append(s[start_idx:])
    return ''.join(result)