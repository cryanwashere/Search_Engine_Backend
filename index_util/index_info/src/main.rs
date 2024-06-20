use std::fs;
use std::io;
use std::io::{stdout, Write};
use std::path::{Path, PathBuf};
use std::fs::metadata;

fn lsdir(path : &Path) -> io::Result<Vec<PathBuf>>
/*
    Given a directory, find all of the child directories and files within.
*/
{
    let mut child_paths = Vec::new();
    if !path.is_dir() {
        return Ok(child_paths)
    }
    for entry in fs::read_dir(path)? {
        let entry = entry?;
        let path = entry.path();
        child_paths.push(path.clone());
    }
    return Ok(child_paths);
}

fn fsize(path: &PathBuf) -> io::Result<u64>
/*
    Given a path to a file, find the size of the file (in bytes)
*/
{
    match metadata(path.clone()) {
        Ok(meta) => {
            let file_size = meta.len();
            return Ok(file_size);
        }
        Err(e) => {
            println!("Failed to get the metadata for: {}", path.display());
            return Ok(0);
        }
    }
}
fn recursive_du(path: &Path)
/*
    Recursively search the directory, finding the paths to all the files in the directory
*/
{
    let child_paths = lsdir(path).unwrap();
    for path in child_paths {
        if path.is_dir() {
            recursive_du(&path);
        } else {
            // the path contains a file:
            let file_size = fsize(&path).unwrap();
            const BACKSPACE : char = 8u8 as char; 
            println!("\r[FILE] {} {} bytes", path.display(), file_size);
        } 
    }
}

fn main() 
{
	let args : Vec<String> = std::env::args().collect();
    let dir = Path::new(&args[1]);
    println!("using path: {}", args[1]);
    recursive_du(dir);
}
