#!/usr/bin/env python3
import csv
import sys
from itertools import combinations

samples_file = sys.argv[1]
pairs_outfile = sys.argv[2]

samples = []
with open(samples_file, 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    for line in reader:
        if line != '':
            samples.append(line[0])
print(f"All samples: {samples}")

pairs = list(combinations(samples, 2))

with open(pairs_outfile, 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    for pair in pairs:
        writer.writerow([pair[0], pair[1]])
