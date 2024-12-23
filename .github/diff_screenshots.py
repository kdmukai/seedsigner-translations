import argparse
import glob
import hashlib
import os
import shutil


parser = argparse.ArgumentParser(prog=__name__)

parser.add_argument("before_dir", type=str, help="Directory containing screenshots before the proposed changes")
parser.add_argument("after_dir", type=str, help="Directory containing screenshots after the proposed changes")
parser.add_argument("output_dir", type=str, help="Directory to save the diff screenshots")

args = parser.parse_args()


def list_files_recursively(path: str) -> list[str]:
    return glob.glob(path + "/**/*.png", recursive=True)


def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):  # Read the file in chunks of 8192 bytes
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_pathname_fragment(path):
    # Extract the last 3 parts of the path: en/tools_views/ToolsCalcFinalWordDoneView.png)
    parts = path.split(os.path.sep)
    return os.path.sep.join(parts[-3:])


before_screenshots = {}
paths_before = []
for file in list_files_recursively(args.before_dir):
    screenshot_path = get_pathname_fragment(file)
    before_screenshots[screenshot_path] = compute_file_hash(file)
    paths_before.append(screenshot_path)

only_in_before = []
only_in_after = []
diffs: list[str] = []
paths_after = []
for file in list_files_recursively(args.after_dir):
    screenshot_path = get_pathname_fragment(file)
    if screenshot_path not in before_screenshots:
        only_in_after.append(screenshot_path)

    elif before_screenshots[screenshot_path] != compute_file_hash(file):
        diffs.append(screenshot_path)
    
    paths_after.append(screenshot_path)

only_in_before = set(paths_before) - set(paths_after)

html_output = "<html><body>"
output_dir_before = os.path.join(args.output_dir, "before")
output_dir_after = os.path.join(args.output_dir, "after")
os.makedirs(output_dir_before, exist_ok=True)
os.makedirs(output_dir_after, exist_ok=True)

for screenshot_path in only_in_before:
    print(f"Screenshot only in before: {screenshot_path} | {output_dir_before=}")
    os.makedirs(os.path.join(output_dir_before, os.path.dirname(screenshot_path)), exist_ok=True)
    # shutil.copy(os.path.join(args.before_dir, screenshot_path), os.path.join(output_dir_before, screenshot_path))
    html_output += f"<p>REMOVED {screenshot_path.split(os.path.sep)[-1].split('.')[0]}</br><img src='{os.path.join('before', screenshot_path)}'></p>"

for screenshot_path in only_in_after:
    print(f"Screenshot only in after: {screenshot_path} | {output_dir_after=}")
    os.makedirs(os.path.join(output_dir_after, os.path.dirname(screenshot_path)), exist_ok=True)
    # shutil.copy(os.path.join(args.after_dir, screenshot_path), os.path.join(output_dir_after, screenshot_path))
    html_output += f"<p>ADDED {screenshot_path.split(os.path.sep)[-1].split('.')[0]}</br><img src='{os.path.join('after', screenshot_path)}'></p>"

for screenshot_path in diffs:
    print(f"Screenshot different: {screenshot_path}")
    # Copy both screenshots to the output dir
    os.makedirs(os.path.join(output_dir_before, os.path.dirname(screenshot_path)), exist_ok=True)
    os.makedirs(os.path.join(output_dir_after, os.path.dirname(screenshot_path)), exist_ok=True)
    # shutil.copy(os.path.join(args.before_dir, screenshot_path), os.path.join(output_dir_before, screenshot_path))
    # shutil.copy(os.path.join(args.after_dir, screenshot_path), os.path.join(output_dir_after, screenshot_path))
    html_output += f"<p>{screenshot_path.split(os.path.sep)[-1].split('.')[0]}</br><img src='{os.path.join('before', screenshot_path)}'>&nbsp;<img src='{os.path.join('after', screenshot_path)}'></p>"

if not only_in_after and not only_in_before and not diffs:
    html_output += "<p>No differences found</p>"

html_output += "</body></html>"
with open(os.path.join(args.output_dir, "diffs.html"), "w") as f:
    f.write(html_output)
