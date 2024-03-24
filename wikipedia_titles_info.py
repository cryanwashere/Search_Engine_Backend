

total_titles = 0

# open the title file, and grab a subset of the titles without opening the entire file (there would not be enough RAM to open up the entire file)
with open("/home/wikipedia/enwiki-titles") as f:
    for i, line in enumerate(f):

        total_titles += 1

print(f"number of wikipedia titles: {total_titles}")
      