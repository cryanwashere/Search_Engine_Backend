

total_titles = 0
current_char_titles = 0

current_char = ""

# open the title file, and grab a subset of the titles without opening the entire file (there would not be enough RAM to open up the entire file)
with open("/home/sshfs_volume/wikipedia/enwiki-titles") as f:
    for i, line in enumerate(f):
        total_titles += 1
        current_char_titles += 1
        first_char = line[1:].replace(" ","").replace("\n","").replace("\t","")[0]


        if first_char != current_char:

            print(f"{first_char}: {current_char_titles}",end="\n")
            current_char_titles = 0
            current_char = first_char

print(f"number of wikipedia titles: {total_titles}")
      