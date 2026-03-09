
import sys

file_path = "src/api/consulting_framework_routes.py"

def replace_lines(lines, start, end, message):
    # Adjust for 0-based indexing
    s = start - 1
    e = end
    print(f"Replacing lines {start} to {end} with comment.")
    lines[s:e] = [f"# {message}\n", "\n"]
    return lines

with open(file_path, "r") as f:
    lines = f.readlines()

# Ranges to replace (Stage 5 to 1 to keep indices valid? No, if we modify list, indices shift)
# Actually, if we use a list and slice assignment, subsequent indices shift.
# So we MUST process from bottom to top.

ranges = [
    (1545, 1645, "Routes for Stage 5 are imported from src.api.stage5"),
    (1439, 1542, "Routes for Stage 4 are imported from src.api.stage4"),
    (1334, 1436, "Routes for Stage 3 are imported from src.api.stage3"),
    (1230, 1331, "Routes for Stage 2 are imported from src.api.stage2"),
    (240, 1227, "Routes for Stage 1 are imported from src.api.stage1")
]

# Sort ranges by start line descending
ranges.sort(key=lambda x: x[0], reverse=True)

for start, end, msg in ranges:
    lines = replace_lines(lines, start, end, msg)

with open(file_path, "w") as f:
    f.writelines(lines)

print("Done.")
