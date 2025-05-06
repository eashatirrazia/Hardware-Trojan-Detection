import re
import json

def parse_model_description(model_str):
    convs = []
    pool = None
    readout = "max"  # default assumption
    fc = []

    lines = model_str.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Match repeated convs like (1-4): 4 x GRAPH_CONV...
        repeat_match = re.search(r'\((\d+)-(\d+)\):\s+(\d+)\s+x\s+GRAPH_CONV', line)
        if repeat_match:
            start_idx, end_idx, count = map(int, repeat_match.groups())
            i += 1
            # Skip to the line that contains the GCNConv description
            while i < len(lines) and "GCNConv" not in lines[i]:
                i += 1
            if i < len(lines):
                conv_line = lines[i]
                conv_match = re.search(r'GCNConv\((\d+),\s*(\d+)\)', conv_line)
                if conv_match:
                    in_dim, out_dim = map(int, conv_match.groups())
                    convs.extend([["gcn", in_dim, out_dim]] * count)

        # Match individual GCNConv layers like (0): ...
        elif "GCNConv" in line:
            conv_match = re.search(r'GCNConv\((\d+),\s*(\d+)\)', line)
            if conv_match:
                in_dim, out_dim = map(int, conv_match.groups())
                convs.append(["gcn", in_dim, out_dim])

        # Match SAGPooling
        elif 'SAGPooling' in line:
            sag_match = re.search(r'SAGPooling\(\w+,\s*(\d+),\s*ratio=([\d.]+)', line)
            if sag_match:
                dim, ratio = int(sag_match.group(1)), float(sag_match.group(2))
                pool = ["sagpool", dim, ratio]

        # Match Fully Connected layer
        elif 'Linear' in line:
            fc_match = re.search(r'in_features=(\d+),\s*out_features=(\d+)', line)
            if fc_match:
                fc = [int(fc_match.group(1)), int(fc_match.group(2))]

        i += 1

    return {
        "convs": convs,
        "pool": pool,
        "readout": readout,
        "fc": fc
    }

# Example usage
if __name__ == "__main__":
    model_str = """
    GRAPH2VEC(
      (layers): ModuleList(
        (0): GRAPH_CONV(
          (graph_conv): GCNConv(37, 200)
        )
        (1-4): 4 x GRAPH_CONV(
          (graph_conv): GCNConv(200, 200)
        )
      )
      (pool1): GRAPH_POOL(
        (graph_pool): SAGPooling(GraphConv, 200, ratio=0.8, multiplier=1.0)
      )
      (graph_readout): GRAPH_READOUT()
      (fc): Linear(in_features=200, out_features=2, bias=True)
    )
    """
    result = parse_model_description(model_str)
    print(json.dumps(result, indent=2))
