This is a tool for **detecting dependency errors in Make-Based build system** 

### How to Use This Tool  
1. Setup the configuration file located at `config/config.ini`  
    a. `path section:` specify the directory where the report file will be generated   
    b. `config section:` specify the directories where system files are located, which will be filtered during processing    
2. Enable the syscall which would be traced  
    a. use the `strace` tool to trace the whole build process of a toy program, such as HelloWorld  
    b. identify syscalls that related to file operation, such as `open`, `remove`   
    c. modify the trace command in `src/VeMakeDDG/preprocess.py/generate_profile` function  
    d. modify the parse function in `src/VeMakeDDG/DDG.py/get_process_IOinfo` function  
    note: this repository is work on `Ubuntu 18`
3. run the command  
    a. command format: `python run.py -f /path/to/testprogram -simple`  
    b. `-simple` option enable this tool just to detect issues in building default target  
    c. for more options, refer to `src/run.py`

### Some Test Programs  
VeriBuild Test Programs can be found on [vemakereporter](https://github.com/vemakereporter)