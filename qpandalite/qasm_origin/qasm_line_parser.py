import re

class OpenQASM2_Parser:
	opname = r'([A-Za-z]+)'
    blank = r' *'
    qid = r'q *\[ *(\d+) *\]'
    cid = r'c *\[ *(\d+) *\]'
    comma = r','
    lbracket = r'\('
    rbracket = r'\)'
    parameter = r'(-?\d+(\.\d*)?([eE][-+]?\d+)?)'
    regexp_1q_str = '^' + opname + blank + qid + '$'
    regexp_2q_str = '^' + opname + blank + qid + blank + comma + blank + qid + '$'
    regexp_1q1p_str = ('^' + 
                        opname + blank + 
                        qid + blank +  
                        comma + blank + 
                        lbracket + blank + 
                        parameter + blank + 
                        rbracket + 
                        '$')
    regexp_1q2p_str = ('^' + 
                        opname + blank + 
                        qid + blank +  
                        comma + blank + 
                        lbracket + blank + 
                        parameter + blank + 
                        comma + blank + 
                        parameter + blank + 
                        rbracket +
                        '$')
    regexp_measure_str = ('^' + 
                        r'MEASURE' + blank + 
                        qid + blank + 
                        comma + blank + 
                        cid + 
                        '$')
        
    regexp_control_str = (r'^(CONTROL|ENDCONTROL)' +
                          f'(({blank}{qid}{blank}{comma})*{blank}{qid}{blank})' + 
                          '$')
    
    regexp_1q = re.compile(regexp_1q_str)
    regexp_2q = re.compile(regexp_2q_str)
    regexp_1q1p = re.compile(regexp_1q1p_str)
    regexp_1q2p = re.compile(regexp_1q2p_str)
    regexp_meas = re.compile(regexp_measure_str)
    regexp_control = re.compile(regexp_control_str)
    regexp_qid = re.compile(qid)

    def __init__(self):
        pass