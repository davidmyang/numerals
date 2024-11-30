from typing import Set, List, Dict
import pandas as pd

ARTIFICIAL_PATH = "data/artificial_language_grammars.csv"
NATURAL_PATH = "data/natural_language_grammars.csv"

def generate_numbers(target_range: range, digits: list, bases: list, monomorphemic: list, 
                     curr_bases: list, number_addition_maxs: list, 
                     number_subtraction_maxs: list, phrase_subtraction: int, 
                     exceptions: list) -> Dict[int, List[str]]:
    """
    Generates constructions for numbers in the target range using the given grammar.
    """
    # Initialize results dictionaries. results can store multiple possible constructions of a number.
    # final_results stores the final construction, so there should only be one per number.
    results = {i: set() for i in target_range}
    final_results = [''] * (len(target_range) + 1)

    # Initialize exceptions dictionary which maps number to a list containing the range and construction.
    exceptions_dict = {exception[0]: [exception[1], exception[2]] for exception in exceptions}

    def get_curr_base(number: int):
        """
        Gets the current base for the given argument.
        """
        possible_bases = []
        
        for elem in curr_bases:
            if in_ranges(number, elem[0]):
                possible_bases.append(elem[1])

        if len(possible_bases) > 0:
            return possible_bases[-1]
        return -1
    
    def get_curr_max_addend(number: int):
        """
        Gets the current max addend (max NUMBER allowed in phrase + NUMBER) 
        for the given argument.
        """
        for elem in number_addition_maxs:
            if in_ranges(number, elem[0]):
                return elem[1]
        return -1
    
    def get_curr_max_subtrahand(number: int):
        """
        Gets the current max subtrahand (max NUMBER allowed in phrase - NUMBER) 
        for the given argument.
        """
        for elem in number_subtraction_maxs:
            if in_ranges(number, elem[0]):
                return elem[1]
        return -1

    def add_construction(number: int, expr: str, is_final = False):
        """
        Adds a new construction (expr) for the given number.
        is_final determines if this is the final construction of the number.
        """
        if not is_final and number in results:
            results[number].add(expr)
        elif is_final and len(final_results[number]) == 0:
            final_results[number] = expr

    def add_phrase(n: int, cur_base: int):
        """
        Builds phrases for the language.
        """
        if n % cur_base == 0:
            phrases.add(n)
            if n in exceptions_dict and in_ranges(n, exceptions_dict[n][0]):
                add_construction(n, exceptions_dict[n][1], is_final=True)
            if n in monomorphemic:
                return

            quotient = n // cur_base
            if results[quotient] and quotient > 1:
                quotient_constructions = results[quotient].copy()
                base_constructions = results[cur_base].copy()
                if quotient in exceptions_dict and in_ranges(n, exceptions_dict[quotient][0]):
                    quotient_constructions = [exceptions_dict[quotient][1]]
                if cur_base in exceptions_dict and in_ranges(n, exceptions_dict[cur_base][0]):
                    base_constructions = [exceptions_dict[cur_base][1]]
                for result in quotient_constructions:
                    for base_result in base_constructions:
                        expr = f"({result} * {base_result})"
                        add_construction(n, expr)

    # Add Digits
    for d in digits:
        add_construction(d, str(d))
        if d in exceptions_dict:
            add_construction(d, exceptions_dict[d][1], is_final=True)

    # Add M
    for b in bases:
        add_construction(b, str(b))
        if b in exceptions_dict:
            add_construction(b, exceptions_dict[b][1], is_final=True)

    # Add monomorphemics
    for mm in monomorphemic:
        add_construction(mm, str(mm))
        if mm in exceptions_dict:
            add_construction(mm, exceptions_dict[mm][1], is_final=True)

    # Build Phrases
    phrases = set([])

    for b in bases:
        phrases.add(b)

    # Phrase = Number * M
    for n in target_range:  
        cur_base = get_curr_base(n)
        if cur_base == -1:
            continue
        add_phrase(n, cur_base)
    
    # NOTE: Commenting this out for now since we don't have trustworthy data
    # new_phrases = set([])
    # for phrase in phrases:
    #      # Phrase Subtraction: Phrase = Phrase - X
    #     if phrase_subtraction:
    #             new_phrase = phrase - phrase_subtraction[0]
    #             if new_phrase in target_range:
    #                 new_phrases.add(new_phrase)
    #                 for phrase_expr in results[phrase]:
    #                     expr = f"({phrase_expr} - {phrase_subtraction[0]})"
    #                     add_construction(phrase - phrase_subtraction[0], expr)
    
    # for phrase in new_phrases:
    #     phrases.add(phrase)

    def generate_constructions(n: int):
        """
        Generates constructions for the given number.
        """
        # No need to try to construct monomorphemic numbers
        if n in monomorphemic:
            return

        # Get current base, max addend, and max subtrahand
        cur_base = get_curr_base(n)
        cur_max_addend = get_curr_max_addend(n)
        cur_max_subtrahand = get_curr_max_subtrahand(n)

        if cur_base == -1:
            return

        # Handle global exceptions
        if n in exceptions_dict:
            if exceptions_dict[n][0][0] == 1 and exceptions_dict[n][0][1] == 100:
                add_construction(n, exceptions_dict[n][1])
            return
        
        # NOTE: Need to do this again for a language like Cahuilla which can't correctly construct 60 = (5 + 1) * 10
        # in the first pass above. This is because it doesn't know that 6 = 5 + 1 since 6 is not in digits or bases.
        
        # Phrase = Number * M
        add_phrase(n, cur_base)

        # Loop through phrases to build numbers from addition and subtraction
        for phrase in phrases:
            # Addition: Phrase + Number
            if phrase % cur_base == 0 and 0 < n - phrase < cur_max_addend:              
                addend = n - phrase
                phrase_constructions = results[phrase]
                addend_constructions = results[addend]

                if phrase in exceptions_dict and in_ranges(n, exceptions_dict[phrase][0]):
                    phrase_constructions = [exceptions_dict[phrase][1]]
                if addend in exceptions_dict and in_ranges(n, exceptions_dict[addend][0]):
                    addend_constructions = [exceptions_dict[addend][1]]
                for phrase_expr in phrase_constructions:
                    for addend_expr in addend_constructions:
                        expr = f"({phrase_expr} + {addend_expr})"
                        add_construction(n, expr)

            # Subtraction: Phrase - Number
            if cur_max_subtrahand > 0:
                if phrase % cur_base == 0 and 0 < phrase - n < cur_max_subtrahand:
                    subtrahand = phrase - n
                    phrase_constructions = results[phrase]
                    subtrahand_constructions = results[subtrahand]

                    if phrase in exceptions_dict and in_ranges(n, exceptions_dict[phrase][0]):
                        phrase_constructions = [exceptions_dict[phrase][1]]
                    if subtrahand in exceptions_dict and in_ranges(n, exceptions_dict[subtrahand][0]):
                        subtrahand_constructions = [exceptions_dict[subtrahand][1]]
                    for phrase_expr in phrase_constructions:
                        for subtrahand_expr in subtrahand_constructions:
                            expr = f"({phrase_expr} - {subtrahand_expr})"
                            add_construction(n, expr)
        

    # Generate constructions for numbers 1 - 100    
    for n in target_range:
        generate_constructions(n)
    
    for n in target_range:
        constructions = results[n]
        #print(constructions)
        if len(constructions) == 1 and len(final_results[n]) == 0:
            final_results[n] = constructions.pop()
    return final_results


def in_ranges(number, range):
    """
    Returns if the given number is within the given range. Range can be a sublist of more ranges
    and each range is structured as [start, stop, increment] where stop is non-inclusive
    and increment is an optional parameter.
    """
    if not range:
        return False
    if not isinstance(range[0], list) and number < range[0]:
        return False
    
    # Check if range contains a list of ranges
    if isinstance(range[0], list):
        inside_range = False
        for sub_range in range:
            inside_range = inside_range or in_ranges(number, sub_range)
        return inside_range
    
    if range[0] <= number < range[1]:
        return True
    
    # Handle optional increment parameter here
    if len(range) == 3:
        start, stop, inc = range
        relative_number = (number - start) % inc
        return 0 <= relative_number < (stop - start)
    return False

def main():
    # Read language-specifics from file
    language_grammars = pd.read_csv(NATURAL_PATH)
    language_constructions = pd.DataFrame(columns=['language', 'number', 'constructions'])
    target_range = range(1, 100)

    nrows = language_grammars.shape[0]
    for i in range(nrows):
        # Get row
        language = language_grammars.iloc[i]

        # Read each column
        name = language['name']
        digits = set(eval(language['digits']))
        bases = set(eval(language['bases']))
        monomorphemic = set(eval(language['monomorphemics']))
        curr_bases = eval(language['curr_bases'])
        number_addition_maxs = eval(language['number_addition_max'])
        number_subtraction_maxs = eval(language['number_subtraction_max'])
        phrase_subtraction = eval(language['phrase_subtraction'])
        exceptions = eval(language['exceptions'])

        # Generate numbers in range for specific language
        final_results = generate_numbers(target_range, digits, bases, monomorphemic, curr_bases,
                                        number_addition_maxs, number_subtraction_maxs, 
                                        phrase_subtraction, exceptions)
        
        print(f"language {i}: {name}")
        for i in target_range:
            form = final_results[i]
            if len(form) == 0:
                form = "ERR"
            language_constructions = pd.concat([language_constructions, pd.DataFrame([[name, i, form]], 
                                                columns=language_constructions.columns)], ignore_index=True)
    
    # Write data to csv file
    language_constructions.to_csv("data/language_specific_constructions.csv", index=False)

if __name__ == "__main__":
    main()