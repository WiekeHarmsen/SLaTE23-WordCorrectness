import helper_scripts.constants as constant


"""
This function checks whether the current pcu is the last non "-" PCU.
pcu_idx   current pcu index
target_pcus  list of target pcus
x         which postition to check (-1 is last char, -2 is one but last char, etc.)
"""
def is_xth_but_last_letter(pcu_idx, target_pcus, x):
    remaining_parts = target_pcus[pcu_idx+1:]
    remaining_chars = "".join(remaining_parts)
    remaining_letters = remaining_chars.replace("-", "")
    
    return (len(remaining_letters)+1)*-1 == x
    


"""
This function detects miniaturization (geminaatdelging). Example: achttien (target), achtien (original)
before_pcus  pcus before error
after_pcus   pcus after error
morphemes    list of morphemes of word
del_char     letter that is not written
"""
def geminaatdelging(before_pcus, after_pcus, morphemes, del_char):
    before = "".join(before_pcus)
    after = "".join(after_pcus)
    
    before = before.replace("-", "").lower()
    before = before.replace("|", "")
    after = after.replace("-", "").lower()
    after = after.replace("|", "")
    
    before_found = False
    after_found = False
    
    for m in morphemes:
        nr = 0
        if len(m)>2:
            nr = 3
        elif len(m)==2:
            nr = 2
        elif len(m)==1:
            nr = 1

        if before[-(nr-1):]+del_char == m[-nr:]:
            before_found = True
        if del_char + after[:nr-1] == m[:nr]:
            after_found = True         
    return before_found and after_found



"""
This function checks whether a phoneme corresponding to the target pcu is present before or after the error.
pcu_idx   current pcu index
target_pcus  list of target pcus
target_phons list of target phonemes
"""
def same_phon_around_idx(target_pcus, pcu_idx, target_phons):
    obstruent_pairs = [["b", "p"], ["v", "f"], ["z", "s"]]
    
    pair = 0
    
    #find target pcu in obstruent pairs
    target_pcu = target_pcus[pcu_idx]
    for i in range(len(obstruent_pairs)):
        for j in range(len(obstruent_pairs[i])):
            if target_pcu == obstruent_pairs[i][j]:
                pair = i
    
    #check if letter from same pair is before or after target_pcu
    target_pcu_before = target_pcus[pcu_idx-1]
    target_pcu_after = target_pcus[pcu_idx+1]
    
    stat1 = (target_pcu_before in obstruent_pairs[pair] and target_pcu_before != target_pcu)
    stat2 = (target_pcu_after in obstruent_pairs[pair] and target_pcu_after != target_pcu)
    
    phon_stat1 = target_phons[pcu_idx] == "-" or target_phons[pcu_idx-1] == "-"
    phon_stat2 = target_phons[pcu_idx] == "-" or target_phons[pcu_idx+1] == "-"
    
    return (stat1 and phon_stat1) or (stat2 and phon_stat2)



"""
This function checks whether char x is at the end of a morpheme.
pcu_idx    current pcu index
target_pcus   list of target pcus
morphemes  list of morphemes
x          last letter
"""
def at_end_of_morpheme(pcu_idx, target_pcus, morphemes, lemma, x):
        
    before = "".join(target_pcus[:pcu_idx])
    before = before.replace("-", "").lower()
    before = before.replace("|", "")
    
    before_found = False
    
    for m in morphemes:
        nr = 0
        if lemma in constant.strong_verbs:
            nr = 1
        if len(m)>2:
            nr = 3
        elif len(m)==2:
            nr = 2
        elif len(m)==1:
            nr = 1
        
        if before[-(nr-1):]+x == m[-nr:]:
            before_found = True     
    return before_found



"""
This function checks whether assimilation of stem is happening in the error.
target_pcu   the target pcu
original_pcu   the original pcu
target_phon  the target phoneme
"""
def check_for_stem_assimilation(target_pcu, original_pcu, target_phon, orth_found, error_found):
    ### Errors ###
    #target in voiced and original in unvoiced
    if target_pcu in constant.cons_dict["voiced_chars"] and original_pcu in constant.cons_dict["unvoiced_chars"]:
        
        #get index of original in unvoiced
        idx_original_unvoiced = constant.cons_dict["unvoiced_chars"].index(original_pcu)
        
        #check if char in voiced at this index is pcu_target
        if constant.cons_dict["voiced_chars"][idx_original_unvoiced] == target_pcu:
            
            #check if target_phon is also unvoiced, just as the original
            unvoiced_phon = constant.cons_dict["unvoiced_phons"][idx_original_unvoiced]
            if target_phon == unvoiced_phon:
                error_found = "MoAs1a" 
    
    #target in unvoiced and original in voiced
    elif target_pcu in constant.cons_dict["unvoiced_chars"] and original_pcu in constant.cons_dict["voiced_chars"]:
        
        #get index of target in unvoiced
        idx_target_unvoiced = constant.cons_dict["unvoiced_chars"].index(target_pcu)
        
        #check if char in voiced at this index is pcu_original
        if constant.cons_dict["voiced_chars"][idx_target_unvoiced] == original_pcu:
            
            #check if target_phon is also voiced, just as the original
            voiced_phon = constant.cons_dict["voiced_phons"][idx_target_unvoiced]
            if target_phon == voiced_phon:
                error_found = "MoAs1b";
                
    ### Orthographic properties ###
    #target_pcu is voiced, but target_phon is unvoiced
    if target_pcu in constant.cons_dict["voiced_chars"]:
        
        if target_pcu != "g":
        
            #Get index of target in voiced chars
            idx_target_voiced = constant.cons_dict["voiced_chars"].index(target_pcu)

            #Get corresponding phoneme
            target_phon_unvoiced = constant.cons_dict["unvoiced_phons"][idx_target_voiced]

            if target_phon_unvoiced == target_phon:
                orth_found = "MoAs1"
        
        elif target_pcu == "g":

            for idx_target_voiced in [2,5,6]:

                #Get corresponding phoneme
                target_phon_unvoiced = constant.cons_dict["unvoiced_phons"][idx_target_voiced]

                if target_phon_unvoiced == target_phon:
                    orth_found = "MoAs1"

    #target_pcu is unvoiced, but target_phon is voiced        
    elif target_pcu in constant.cons_dict["unvoiced_chars"]:
        
        #Get index of target in voiced chars
        idx_target_unvoiced = constant.cons_dict["unvoiced_chars"].index(target_pcu)
        
        #Get corresponding phoneme
        target_phon_voiced = constant.cons_dict["voiced_phons"][idx_target_unvoiced]
        
        if target_phon_voiced == target_phon:
            orth_found = "MoAs1"
        
    return orth_found, error_found

 
"""
This function is used for wrongly written composition words, either splitted by a space or a "n".
before_pcus  list of pcus before splitter
after-pcus   list of pcus after splitter
morphemes    list of morphemes
splitters    character on which is split: "|" (space) or "n"
"""
def n_or_space_between_two_morphemes(before_pcus, after_pcus, morphemes, splitter):
    #Concatenate items of pcus list
    before = "".join(before_pcus)
    after = "".join(after_pcus)
    
    #Preprocess before and after strings
    before = before.replace("-", "").lower()
    before = before.replace("|", "")
    after = after.replace("-", "").lower()
    after = after.replace("|", "")
    
    before_found = False
    after_found = False
    
    #Check if one/two/three characters before and after insertion of space match begin/end morphemes.
    for m in morphemes:
        nr = 0
        if len(m)>2:
            nr = 3
        elif len(m)==2:
            nr = 2
        elif len(m)==1:
            nr = 1

        if splitter == "|":            
            if before[-nr:] == m[-nr:]:
                before_found = True

            if after[:nr] == m[:nr]:
                after_found = True
                
        elif splitter == "n":
            if before[-(nr-1):]+"n" == m[-nr:]:
                before_found = True
            
            if after[:nr] == m[:nr]:
                after_found = True
        
        elif splitter == "s" and len(after)>=3:
            if before[-(nr-1):]+"s" == m[-nr:] or before[-nr:] == m[-nr:]:
                before_found = True
            
            if after[:nr] == m[:nr]:
                after_found = True
                
    return before_found and after_found
