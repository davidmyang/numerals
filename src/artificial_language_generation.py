import random
import pandas as pd

# Max number of digits, bases, and monomorphemics for an artificial language
MAX_DIGITS = 20
MAX_NUM_BASES = 5
MAX_MONOMORPHEMICS = 5

NUM_LANGUAGES = 10

def generate_digits():
    num = random.randint(1, MAX_DIGITS)
    digits = list(range(1, num + 1))
    return digits

def generate_bases(digits):
    # Must include number after last digit as a base, otherwise, impossible to construct all numbers in range
    bases = [digits[-1] + 1]
    num = random.randint(1, MAX_NUM_BASES)
    for i in range(num):
        base = random.randint(digits[-1] + 2, 100)
        bases.append(base)
    return sorted(bases)

def generate_monomorphemics(digits, bases):
    monomorphemics = []
    num = random.randint(0, MAX_MONOMORPHEMICS)
    for i in range(num):
        monomorphemic = random.randint(digits[-1] + 1, 100)
        while (monomorphemic in bases):
            monomorphemic = random.randint(digits[-1] + 1, 100)
        monomorphemics.append(monomorphemic)
    return sorted(monomorphemics)

def generate_multiplication_rule(bases):
    multiplication_rule = []
    for i in range(1, len(bases)):
        multiplication_rule.append(bases[i])
        multiplication_rule.append(bases[i - 1])
        i += 2
    multiplication_rule.append(100)
    multiplication_rule.append(bases[-1])
    
    return multiplication_rule


def generate_language(idx, language_grammars):
    name = "artificial_language_" + str(idx)
    # Generate lexicon
    digits = generate_digits()
    bases = generate_bases(digits)
    monomorphemics = generate_monomorphemics(digits, bases)

    # Generate grammar rules
    multiplication_rule = addition_rule = generate_multiplication_rule(bases)

    num_sub_rule = phrase_sub_rule = multiplier = exceptions = []

    new_row = pd.DataFrame([[name, digits, bases, monomorphemics, multiplication_rule,
                             addition_rule, num_sub_rule, phrase_sub_rule,
                             multiplier, exceptions]],
                           columns=language_grammars.columns)
    language_grammars = pd.concat([language_grammars, new_row], ignore_index=True)
    return language_grammars

def main():
    language_grammars = pd.DataFrame(columns=["name","digits","bases","monomorphemics","curr_bases","number_addition_max",
                                              "number_subtraction_max","phrase_subtraction","multiplier","exceptions"])

    for i in range(NUM_LANGUAGES):
        language_grammars = generate_language(i, language_grammars)

    # Write data to csv file
    language_grammars.to_csv("data/artificial_language_grammars.csv", index=False)

if __name__ == "__main__":
    main()