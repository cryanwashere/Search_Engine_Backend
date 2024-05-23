import os

'''
 
    The purpose of this script is to open the wikipedia titles file, and split it into multiple smaller text files. This will make it easier to coordinate crawling the wikipedia pages in parallel

'''
counter = 0
last_save = 9800000
current = 0
file_str = ""
with open("/home/sshfs_volume/wikipedia/enwiki-titles") as f:

    print(f"opened enwiki-titles file")
    for i, line in enumerate(f):
        #line[1:].replace(" ","").replace("\n","").replace("\t","")


        file_str += line
        counter += 1
        current += 1

        if counter >= 50000 and current >= last_save:

            file_path = os.path.join("/home/sshfs_volume/wikipedia/enwiki-titles_split/", f"enwiki-titles{last_save}-{current}.txt")
            print(f"saving titles: {last_save} -> {current} to {file_path}")

            with open(file_path, "w") as f:
                f.write(file_str)
            
            file_str = ''
            last_save = current
            counter = 0
print("finished")


