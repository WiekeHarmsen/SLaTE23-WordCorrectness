import re
import helper_scripts.adagt as adagt 
import helper_scripts.constants as constants

"""
This function obtains the alignments of the target and original text.
"""
def get_ADAGT_alignments(target_text, original_text):
    # Split text in parts (necessary for the ADAGT algorithm)
    target_text_parts, original_text_parts = textToParts(target_text, original_text)

    target_text_align = ""
    original_text_align = ""
    total_dist_score = 0

    for s in range(len(target_text_parts)):
        # Align the target and original part
        dist_score, _, _, _, target_text_part_align, original_text_part_align = adagt.align_dist(target_text_parts[s], original_text_parts[s])

        # Paste parts together again
        if s > 0:
            target_text_align = target_text_align + " " + target_text_part_align
            original_text_align = original_text_align + " " + original_text_part_align
        else:
            target_text_align = target_text_part_align
            original_text_align = original_text_part_align

        total_dist_score += dist_score
    
    return target_text_align, original_text_align, total_dist_score


"""
# This function splits a text in shorter parts.
# This is necessary, because the ADAGT alogrithm is not able to handle long strings of characters.
# First I try to split the text at periods (end of sentence). 
# If this is not possible (for example because the text does not contain periods), I split after 150 characters.
"""
def textToParts(target_text, original_text):
    max_length = 50
    if len(target_text) <= max_length and len(original_text) <= max_length:
        return [target_text], [original_text]

    target_text_sent = []
    original_text_sent = []
    begin = 0

    # Check if text contains right amount of dots to split the text at the dots in text
    # on average every 150 characters a dot
    desired_nr_of_dots = int(len(original_text)/max_length)+1
    actual_nr_of_dots = original_text.count(".")

    # If text doesn't contain enough periods
    if(original_text.find(". ", begin, -1) == -1) or (desired_nr_of_dots >= actual_nr_of_dots):
        length = len(original_text)
        nr_of_splits = int(length/max_length)

        for split_idx in range(nr_of_splits):

            # We need to make a split at around_idx
            around_idx = (split_idx+1)*max_length

            for trial_idx in range(10):
                # find first space near around_idx in original
                space_idx_original = original_text.find(" ", around_idx, around_idx+10)

                # save slice
                original_slice = original_text[space_idx_original-3:space_idx_original+3]

                # try to find slice in target_original
                if(target_text.find(original_slice, space_idx_original-30, space_idx_original+30) != -1):
                    # If found, save space_idx_target
                    space_idx_target = target_text.find(original_slice, space_idx_original-30, space_idx_original+30)+3

                    # insert dollar sign to replace space
                    original_text = original_text[:space_idx_original] + \
                        "$"+original_text[space_idx_original+1:]
                    target_text = target_text[:space_idx_target] + \
                        "$"+target_text[space_idx_target+1:]
                    break
                else:
                    if trial_idx == 1:  # odd numbers
                        space_idx_original = original_text.find(" ", around_idx-10, around_idx)
                    elif trial_idx >= 2:
                        space_idx_original = original_text.find(" ", around_idx+((trial_idx-1)*10), around_idx+(trial_idx*10))

        # split opstellen at $
        original_text_sent = original_text.split("$")
        target_text_sent = target_text.split("$")

    else:
        while len(original_text) > 0 and original_text.find(". ", begin, -1) != -1:

            # Search first position of . in original
            idx = original_text.find(". ", begin, -1)

            # Save five chars before and five chars after
            dot_slice = original_text[idx-3:idx+3]

            # Find dot slice in target
            if(target_text.find(dot_slice, begin-10, idx+10) != -1):

                # dot slice is found
                idx_target = target_text.find(dot_slice, begin-10, idx+10) + 3

                # split both texts.
                sent_target = target_text[:idx_target+1]
                target_text = target_text[idx_target+2:]
                sent_original = original_text[:idx+1]
                original_text = original_text[idx+2:]

                # Add sent_target and sent_original to lists
                target_text_sent.append(sent_target)
                original_text_sent.append(sent_original)
                begin = 0

            else:
                # idx is not found in target, we should find next idx in original
                begin = idx+1

        # Add remaining parts to target_text_sent and original_text_sent
        target_text_sent.append(target_text)
        original_text_sent.append(original_text)

    return target_text_sent, original_text_sent


"""
Get alignments of target and original text (strings)
"""
def get_alignments(target, original):
    
    # Get ADAGT alignments
    target_align, original_align, _ = get_ADAGT_alignments(target, original)

    # Get alignments in correct format
    aligned_words = changeFormatToWordList(target_align, original_align)
    
    return aligned_words


"""
This function cleans the original part of text.
"""
def clean_original_bsopstel(text):
    text = text.replace("\n", " ")

    # Replace & with "en"
    text = text.replace("&", "en")

    # Remove unreadable words marked with <o> or <O>
    text = text.replace("<o>", "")
    text = text.replace("<O>", "")

    # Remove <a> tags (used when text is left or right is truncated by wrong copying)
    text = text.replace("<a>", "")
    text = text.replace("<A>", "")

    # Remove personal information marked with <*> tags
    text = re.sub("<\*>", "", text)

    # Remove << >> tags (letters between these tags are written in mirror image)
    text = re.sub("<<", "", text)
    text = re.sub(">>", "", text)

    # Remove text between <d> tags
    text = re.sub("<d>[^<]*<d>\s", "", text)
    text = re.sub("<d>[^<]*<d>", "", text)

    # Remove text between <D> tags
    text = re.sub("<D>[^<]*<D>\s", "", text)
    text = re.sub("<D>[^<]*<D>", "", text)

    # Replace two or more spaces with one space
    text = re.sub("\s+", " ", text)

    return text


"""
Creates a list of lists. 
Each list containing the n-pair (counter throughout the lists), target, target_align, original_align, and correct (boolean).
Target_align and original_align given are strings. They are split at spaces.
"""
def changeFormatToWordList(target_align, original_align):
    word_list = []

    start_idx = 0
    end_idx = 0
    target_list = []
    original_list = []

    # Align original contains no word boundaries and align target contains no word boundaries
    if original_align.find(" ") == -1 and target_align.find(" ") == -1:
        target_list.append(target_align)
        original_list.append(original_align)

    # Align original contains no word boundaries
    elif original_align.find(" ") == -1:
        while target_align.find(" ", start_idx) != -1:
            first_wbn = target_align.index(" ", start_idx)
            target_list.append(target_align[start_idx:first_wbn])
            original_list.append(original_align[start_idx:first_wbn])
            start_idx = first_wbn+1
        target_list.append(target_align[start_idx:])
        original_list.append(original_align[start_idx:])

    # Align target contains no word boundaries
    elif target_align.find(" ") == -1:
        target_list.append(target_align)
        original_list.append(original_align)

    # Align original contains word boundaries
    else:
        for i in range(len(target_align)):
            if target_align[i] == " ":
                end_idx = i

                # First word in target
                if start_idx == 0:
                    target_list.append(target_align[start_idx:end_idx])
                    original_list.append(original_align[start_idx:end_idx])

                # Middle word in target
                elif start_idx != 0:
                    target_list.append(target_align[start_idx+1:end_idx])
                    original_list.append(original_align[start_idx+1:end_idx])

                # last word in target
                if(target_align.find(" ", end_idx+1) == -1):
                    target_list.append(target_align[end_idx+1:].replace(" ", ""))
                    original_list.append(original_align[end_idx+1:])

                start_idx = end_idx

    for i in range(len(target_list)):
        row = []
        row.append(i)
        row.append(target_list[i].replace(constants.zero_char, ""))
        row.append(target_list[i])
        row.append(original_list[i])

        if original_list[i] == target_list[i].replace(constants.zero_char, ""):
            row.append(1)
        else:
            row.append(0)

        word_list.append(row)
    return word_list



def main():

    target = "hoi4"
    original = "€hallo7"
    aligned_words = get_alignments(target, original)
    print(aligned_words)

if __name__ == '__main__':
    main()
