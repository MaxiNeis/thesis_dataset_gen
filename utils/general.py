
def is_valid_citation(cgpt_result_dict):
    # Check if all citations are valid
    # Return True if citations are valid -> no the same value for every key
    # Return False if all citations are the same
    res = False
 
    test_val = list(cgpt_result_dict.values())[0]
    
    for ele in cgpt_result_dict:
        if cgpt_result_dict[ele] != test_val:
            res = True
            break
    return res