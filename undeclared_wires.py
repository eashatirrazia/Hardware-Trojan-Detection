import re
import argparse
import logging
import os

def find_undeclared_wires(verilog_code):
    """
    Finds undeclared wires in all modules of a Verilog code.

    Args:
        verilog_code (str): The Verilog code as a string.

    Returns:
        dict: A dictionary where keys are module names and values are lists of undeclared wires.
              Returns an empty dict if no modules are found or if no undeclared wires exist.
    """
    modules = {}
    module_matches = re.finditer(r'module\s+([a-zA-Z0-9_]+)\s*\(.*?\);', verilog_code, re.DOTALL)
    endmodule_matches = re.finditer(r'endmodule', verilog_code, re.DOTALL)

    if len(list(module_matches)) != len(list(endmodule_matches)):
        logging.error("Unbalanced 'module' and 'endmodule' keywords. Skipping file.")
        return {}

    module_matches = re.finditer(r'module\s+([a-zA-Z0-9_]+)\s*\(.*?\);', verilog_code, re.DOTALL)

    for module_match in module_matches:
        module_name = module_match.group(1)
        module_start = module_match.start()
        module_end = verilog_code.find('endmodule', module_start) + len('endmodule')
        module_code = verilog_code[module_start:module_end]

        try:
            arg_start = module_code.find('(') + 1
            arg_end = module_code.find(')')
            if arg_start > 0 and arg_end > 0:
                arg_string = module_code[arg_start:arg_end]
                arguments = [arg.strip() for arg in arg_string.split(',')]
            else:
                arguments = []
        except Exception as e:
            logging.error(f"Error extracting arguments for module {module_name}: {e}")
            arguments = []

        declared_wires = []
        wire_matches = re.finditer(r'wire\s+([\[\]:\w\s,]+);', module_code)
        for wire_match in wire_matches:
            wire_string = wire_match.group(1).strip()
            wire_string = re.sub(r'\[.*?\]', '', wire_string)
            wires = [w.strip() for w in wire_string.split(',')]
            declared_wires.extend(wires)

        used_signals = []
        signal_matches = re.finditer(r'\.\w+\s*\(\s*({[\[\]\w\s,]+}|[\[\]\w]+)\s*\)', module_code)
        for signal_match in signal_matches:
            signal_group = signal_match.group(1).strip()
            signal_group = re.sub(r'\[.*?\]', '', signal_group) # remove any square brackets
            if '{' in signal_group:
                # Split the signals within the curly braces
                signals = [s.strip() for s in signal_group.replace('{', '').replace('}', '').split(',')]
                used_signals.extend(signals)
            else:
                used_signals.append(signal_group)

        used_signals = list(set(used_signals))
        undeclared_wires = [signal for signal in used_signals if signal not in arguments and signal not in declared_wires]
        modules[module_name] = undeclared_wires

    return modules

def print_undeclared_wires(undeclared_wires_dict):
    """
    Prints the undeclared wires for each module.

    Args:
        undeclared_wires_dict (dict): A dictionary where keys are module names and
                                      values are lists of undeclared wires.
    """
    if not undeclared_wires_dict:
        logging.info("No undeclared wires found in any module.")
        print("No undeclared wires found in any module.")
        return

    for module_name, undeclared_wires in undeclared_wires_dict.items():
        if undeclared_wires:
            logging.info(f"module {module_name}")
            logging.info(f"wire {', '.join(undeclared_wires)};")
            logging.info("\n==============================\n")

            print(f"module {module_name}")
            print(f"wire {', '.join(undeclared_wires)};")
            print("\n==============================\n")
        else:
            logging.info(f"Module {module_name}:")
            logging.info("  No undeclared wires.")
            logging.info("\n==============================\n")

            print(f"Module {module_name}:")
            print("  No undeclared wires.")
            print("\n==============================\n")



def insert_undeclared_wires(verilog_file, undeclared_wires_dict):
    """
    Inserts the undeclared wire declarations into the Verilog file,
    limiting each line to a maximum of 10 wires.

    Args:
        verilog_file (str): Path to the Verilog file.
        undeclared_wires_dict (dict): A dictionary where keys are module names and
                                      values are lists of undeclared wires.
    """
    try:
        with open(verilog_file, 'r+') as f:
            verilog_code = f.read()
            f.seek(0)  # Reset file pointer to the beginning

            for module_name, undeclared_wires in undeclared_wires_dict.items():
                if undeclared_wires:
                    # Construct the wire declaration string with a maximum of 10 wires per line
                    wire_lines = []
                    for i in range(0, len(undeclared_wires), 10):
                        line_wires = undeclared_wires[i:i+10]
                        wire_lines.append(f"wire {', '.join(line_wires)};")
                    wire_declaration = "\n".join(wire_lines) + "\n"

                    # Find the module definition line
                    module_def_match = re.search(r'module\s+' + re.escape(module_name) + r'\s*\(.*?\);', verilog_code, re.DOTALL)

                    if module_def_match:
                        module_def_end = module_def_match.end()  #find end of module definition
                        # Insert the wire declarations after the semicolon
                        modified_code = verilog_code[:module_def_end] + "\n" + wire_declaration + verilog_code[module_def_end:]
                        verilog_code = modified_code # make the changes
                        logging.info(f"Inserted undeclared wires into module {module_name} in {verilog_file}")
                        print(f"Inserted undeclared wires into module {module_name} in {verilog_file}")

                    else:
                        logging.warning(f"Module {module_name} not found in {verilog_file}.  Skipping insertion for this module.")
                        print(f"Module {module_name} not found in {verilog_file}.  Skipping insertion for this module.")
            f.write(verilog_code) # Write the modified verilog code back to the file.

    except Exception as e:
        logging.error(f"Error inserting undeclared wires: {e}")
        print(f"Error inserting undeclared wires: {e}")



def main():
    """
    Main function to read Verilog code from a file, find undeclared wires,
    print the results, and insert the undeclared wires back into the file.
    """
    parser = argparse.ArgumentParser(description="Find and insert undeclared wires in Verilog code.")
    parser.add_argument("verilog_file", help="Path to the Verilog file")
    args = parser.parse_args()
    verilog_file = args.verilog_file

    log_file_name = os.path.splitext(os.path.basename(verilog_file))[0] + ".log"
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        with open(verilog_file, 'r') as f:
            verilog_code = f.read()
    except FileNotFoundError:
        logging.error(f"Error: File not found at {verilog_file}")
        print(f"Error: File not found at {verilog_file}")
        return
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        print(f"Error reading file: {e}")
        return

    undeclared_wires_dict = find_undeclared_wires(verilog_code)
    print_undeclared_wires(undeclared_wires_dict)  # Print to console and log

    insert_undeclared_wires(verilog_file, undeclared_wires_dict) # Insert the wires.



if __name__ == "__main__":
    main()
