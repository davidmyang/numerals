from typing import Set, List, Dict
import pandas as pd

def generate_numbers(target_range: range, digits: list, M: list, monomorphemic: list, 
                     curr_bases: list, number_addition_maxs: list, 
                     number_subtraction_maxs: list, phrase_subtraction: int, 
                     multiplier: list, exceptions: list) -> Dict[int, List[str]]:
    """
    Generate all possible constructions for numbers in the target range using the given grammar.
    
    Args:
        digits: Set of basic digits allowed in the language
        M: Set of multiplier values allowed in the language
        target_range: Range of numbers to generate constructions for
    
    Returns:
        Dictionary mapping each number to a list of its possible constructions
    """
    # Initialize results dictionary
    results = {i: set() for i in target_range}

    def get_curr_base(number: int):
        i = 0
        while i < len(curr_bases):
            if number < curr_bases[i]:
                return curr_bases[i + 1]
            i += 2
        return -1
    
    def get_curr_max_addend(number: int):
        i = 0
        while i < len(number_addition_maxs):
            if number < number_addition_maxs[i]:
                return number_addition_maxs[i + 1]
            i += 2
        return -1
    
    def get_curr_max_subtrahand(number: int):
        i = 0
        while i < len(number_subtraction_maxs):
            if number < number_subtraction_maxs[i]:
                return number_subtraction_maxs[i + 1]
            i += 2
        return -1

    def get_is_multiplier(number: int):
        return number in multiplier
    
    # Helper function to add a new construction if it's in our target range
    def add_construction(value: int, expr: str):
        if value in results:
            if len(expr.split()) < 20:
                results[value].add(expr)
    
    # Add Digits
    for d in digits:
        add_construction(d, str(d))

    # Add M
    for m in M:
        if not get_is_multiplier(m):
            add_construction(m, str(m))
    
    for mm in monomorphemic:
        add_construction(mm, str(mm))

    # Build Phrases
    phrases = set([])

    for m in M:
        phrases.add(m)

    for n in target_range:
        # Phrase = Number * M
        # Constraint: For all N, M = X in Number * M
        cur_base = get_curr_base(n)
        exception_idx = check_exceptions(n, exceptions)

        if n % cur_base == 0:
            phrases.add(n)
            if exception_idx > -1:
                add_construction(n, exceptions[exception_idx][2])
            quotient = n // cur_base
            if results[quotient]:
                for result in results[quotient]:
                    # if not is_multiplier and "1 *" in result:
                    #     continue
                    expr = f"({result} * {cur_base})"
                    add_construction(n, expr)
    
    new_phrases = set()
    for phrase in phrases:
         # Phrase Subtraction: Phrase = Phrase - X
        if phrase_subtraction:
                new_phrase = phrase - phrase_subtraction[0]
                if new_phrase in target_range:
                    new_phrases.add(new_phrase)
                    for phrase_expr in results[phrase]:
                        expr = f"({phrase_expr} - {phrase_subtraction[0]})"
                        add_construction(phrase - phrase_subtraction[0], expr)
    
    for phrase in new_phrases:
        phrases.add(phrase)

    # Helper function to generate all possible constructions for a number
    def generate_constructions(n: int, depth: int = 0, max_depth: int = 3):
        # Prevent infinite recursion
        if n < 1 or n > 99 or depth > max_depth:
            return []
        if len(results[n]) > 0:
            return results[n]


        constructions = []

        cur_base = get_curr_base(n) 
        cur_max_addend = get_curr_max_addend(n)
        cur_max_subtrahand = get_curr_max_subtrahand(n)
        is_multiplier = get_is_multiplier(n)

        # Phrase = Number * M
        # Constraint: For all N, M = X in Number * M
        '''
        Need to do this again for a language like Fulfulde which can't correctly construct 60 = (5 + 1) * 10
        in the first pass above. This is because it doesn't know that 6 = 5 + 1 since 6 is not in digits or M.
        '''
        if n % cur_base == 0:
            phrases.add(n)
            quotient = n // cur_base
            if results[quotient]:
                for result in results[quotient]:
                    for base_result in results[cur_base]:
                        # if not is_multipler and "*" in result:
                        #     continue
                        expr = f"({result} * {base_result})"
                        add_construction(n, expr)

        for phrase in phrases:
            # Addition: Phrase + Number
            if phrase % cur_base == 0 and 0 < n - phrase < cur_max_addend:
                addend = n - phrase
                for phrase_expr in results[phrase]:
                    for addend_expr in results[addend]:
                        # if not is_multiplier and "1 *" in phrase_expr:
                        #     continue
                        expr = f"({phrase_expr} + {addend_expr})"
                        constructions.append(expr)

            # Subtraction: Phrase - Number
            # Deletion: Delete Phrase - Number
            if cur_max_subtrahand > 0:
                if phrase % cur_base == 0 and 0 < phrase - n < cur_max_subtrahand:
                    subtrahand = phrase - n
                    for phrase_expr in results[phrase]:
                        for subtrahand_expr in results[subtrahand]:
                            # if not is_multiplier and "1 *" in phrase_expr:
                            #     continue
                            expr = f"({phrase_expr} - {subtrahand_expr})"
                            constructions.append(expr)
        
        # Add constructions to results
        for const in constructions:
            add_construction(n, const)

    # Generate constructions of 1 - 100    
    for n in target_range:
        generate_constructions(n)
        
    return results

def in_ranges(number, ranges):
    if not ranges:
        return False
    for start, end in zip(ranges[::2], ranges[1::2]):
        if start <= number < end:
            return True
    return False

def check_exceptions(number, exceptions):
    for i in range(len(exceptions)):
        if in_ranges(number, exceptions[i][0]):
            return i
    return -1

def main():
    # Read language-specifics from file
    language_grammars = pd.read_csv("data/language_specific_grammars.csv", engine="python")
    language_constructions = pd.DataFrame(columns=['language', 'number', 'constructions'])
    target_range = range(1, 100)

    nrows = language_grammars.shape[0]
    for i in range(nrows):
        language = language_grammars.iloc[i]

        name = language['name']
        digits = set(eval(language['digits']))
        M = set(eval(language['M']))
        monomorphemic = set(eval(language['monomorphemic']))
        curr_bases = eval(language['curr_bases'])
        number_addition_maxs = eval(language['number_addition_max'])
        number_subtraction_maxs = eval(language['number_subtraction_max'])
        phrase_subtraction = eval(language['phrase_subtraction'])
        multiplier = eval(language['multiplier'])
        exceptions = eval(language['exceptions'])
        
        results = generate_numbers(target_range, digits, M, monomorphemic, curr_bases,
                                   number_addition_maxs, number_subtraction_maxs, 
                                   phrase_subtraction, multiplier, exceptions)
        print("language " + str(i))

        for num in sorted(results.keys()):
            forms = results[num]
            
            if forms and num < 100:
                # Only get constructions with min complexity. If there are ties, print all ties.
                min_word_count = min(len(form.split()) for form in forms)
                exception_idx = check_exceptions(num, exceptions)
                if exception_idx > -1:
                    substring = exceptions[exception_idx][2]
                    correct_forms = [form for form in forms if substring in form]
                    print(correct_forms)
                    for form in correct_forms:
                        language_constructions = pd.concat([language_constructions, pd.DataFrame([[name, num, form]], 
                                                            columns=language_constructions.columns)], ignore_index=True)
                # elif num not in monomorphemic and in_ranges(num, multiplier):
                #     mul_one_string = "*"
                #     mul_one_forms = [form for form in forms if mul_one_string in form]

                #     max_mul_one_occurences = max(form.count(mul_one_string) for form in forms)
                #     mul_one_forms = [form for form in forms if form.count(mul_one_string) == max_mul_one_occurences]
                #     min_mul_one_word_count = min(len(form.split()) for form in mul_one_forms)
                #     shortest_forms = [form for form in mul_one_forms if len(form.split()) == min_mul_one_word_count]
                #     #mul_forms = [form for form in forms if mul_one_string in form]
                #     for form in shortest_forms:
                #         language_constructions = pd.concat([language_constructions, pd.DataFrame([[name, num, form]], 
                #                                     columns=language_constructions.columns)], ignore_index=True)
                else:
                    shortest_forms = [form for form in forms if len(form.split()) == min_word_count]
                    for shortest_form in shortest_forms:
                        language_constructions = pd.concat([language_constructions, pd.DataFrame([[name, num, shortest_form]], 
                                                        columns=language_constructions.columns)], ignore_index=True)
                
    # Write data to csv file
    language_constructions.to_csv("data/language_specific_constructions.csv", index=False)

if __name__ == "__main__":
    main()