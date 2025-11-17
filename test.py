from dutch_med_hips import HideInPlainSight, PHIType, build_pattern_configs

input_file = "hips_debug_input.txt"

with open(input_file, "r", encoding="utf-8") as f:
    report = f.read()

hips = HideInPlainSight()
report = hips.run(text=report)

outfile = "hips_debug_output.txt"
with open(outfile, "w", encoding="utf-8") as f:
    f.write(report["text"])
