import argparse

# hw_path = "some path.v"  # Placeholder, will be replaced by argparser

def find_modules(hw_path):
    with open(hw_path,'r') as file_in:
        lines = file_in.read().split("\n")

    all_modules_dict={}
    for line in lines:
        words = line.split()
        for word_idx, word in enumerate(words):
            if word == 'module':
                module_name = words[word_idx+1]
                if '(' in module_name:
                    idx = module_name.find('(')
                    module_name = module_name[:idx]
                    all_modules_dict[module_name]= 1

                else:
                    all_modules_dict[module_name]= 0
                
    for line in lines:
        words = line.split()
        for word in words:
            if word in all_modules_dict.keys():
                all_modules_dict[word] += 1
    return all_modules_dict


def extract_verilog_identifiers(file_path):
    identifiers = []
    verilog_datatypes = ["wire", "assign", "input", "output", "reg", "integer", "parameter", "localparam", "module", "else", "if", "end", "begin", "//", "endmodule", "always"] # Add more as needed
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            statements = [s.strip() for s in content.split(';') if s.strip()] # Split by ';', remove empty lines
            for statement in statements:
                parts = statement.split()
                if parts:
                    first_word = parts[0]
                    if first_word not in verilog_datatypes:
                        identifiers.append(first_word)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return list(set(identifiers)) #remove duplicates
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract identifiers from a Verilog file.")
    parser.add_argument("file_path", help="Path to the Verilog file.")

    args = parser.parse_args()

    identifiers = extract_verilog_identifiers(args.file_path)
    modules = find_modules(args.file_path)

    # for i in identifiers:
    #     print(i)
    # print("======")
    # print(modules)

    identifiers_not_in_modules = [i for i in identifiers if i not in modules.keys()]

    print("\nIdentifiers not in modules keys:")
    for identifier in identifiers_not_in_modules:
        print(identifier)

    single_use_modules = {}
    for module, count in modules.items():
        if count == 1:
            single_use_modules[module] = count

    print("\nIdentifiers in modules used only once:")
    for identifier, count in single_use_modules.items():
        print(f"{identifier}: {count}")
