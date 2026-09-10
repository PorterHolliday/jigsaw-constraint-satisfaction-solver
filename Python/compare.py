char_numbers = { 'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 15, 'J': 5, 'K': 14,
                 'O': 6, 'P': 13, 'T': 7, 'U': 12, 'V': 11, 'W': 10, 'X': 9, 'Y': 8 }
index_dict = { 0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 15, 6: 5, 7: 14,
                 8: 6, 9: 13, 10: 7, 11: 12, 12: 11, 13: 10, 14: 9, 15: 8 }

def get_unique_solutions():
    solutions = set()
    file = open("solutions.txt", "r")
    data = file.read()
    solution = [''] * 16
    idx = 0
    for line in data.split("\n"):
        if line == '':
            # 0 should always be first
            solution = solution[solution.index(0):] + solution[:solution.index(0)]
            solutions.add(str(solution))
            solution = [''] * 16
            idx = 0
            continue

        for i in range(5):
            index = i * 6
            char = line[index]
            if not char in char_numbers: continue
            value = char_numbers[char]
            solution[index_dict[idx]] = value
            idx += 1

    return solutions

solutions = get_unique_solutions()
for s in solutions:
    print(s)
print(len(solutions))