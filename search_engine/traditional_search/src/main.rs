use std::collections::HashMap;
use std::collections::HashSet;
use std::fs;


fn main() 
{
    
    let text_sources = ["./txt/gatsby.txt",	"./txt/pg100.txt",	"./txt/pg1342.txt",	"./txt/pg145.txt",	"./txt/pg2641.txt",	"./txt/pg2701.txt",	"./txt/pg73778.txt",	"./txt/pg73782.txt"];
    
    let mut word_lookup : HashMap<String, i32> = HashMap::new();
    
    
    for &text_path in &text_sources {
        
        let mut contents = fs::read_to_string(text_path)
            .expect("Failed to read file");
        
        
        update_word_lookup(contents, &mut word_lookup);
        
    }
        
    // put the word entries into a list, and sort them 
    let mut entries: Vec<(&String, &i32)> = word_lookup.iter().collect();
    entries.sort_by(|a, b| b.1.cmp(a.1)); 
    
    // Print each sorted key-value pair
    for (key, value) in entries {
        println!("{}: {}", key, value);
    } 

    let word_count = word_lookup.keys().len();
    println!("{} words in the word lookup", word_count);
}

fn update_word_lookup(text_sample: String, word_lookup: &mut HashMap<String, i32>)
{
    let mut contents = text_sample.to_lowercase();
    contents = contents.chars().map(|c| {
        if (c.is_alphanumeric() || c == ' ') {
            return c;
        } else {
            return ' ';
        }
    }).collect::<String>();
    
    let mut content_split = contents.split_whitespace().collect::<Vec<&str>>();

    for _word in content_split {
        let word : String = _word.to_string();
        if !(word_lookup.contains_key(&word)) {
            word_lookup.insert(word, 1);
        } else {
            *word_lookup.get_mut(&word).unwrap() += 1;
        }
    }
}