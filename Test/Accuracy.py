import os
import json


def read_key_value_pairs(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    pairs = {}
    for line in lines:
        line = line.strip()
        if line:
            key, value = line.split('：')
            pairs[key] = value
    return pairs


def compare_files(test_file, reference_file):
    test_pairs = read_key_value_pairs(test_file)
    reference_pairs = read_key_value_pairs(reference_file)

    count = 0
    matched_pairs = {}
    for key, value in test_pairs.items():
        if key in reference_pairs and reference_pairs[key] == value:
            count += 1
            matched_pairs[key] = value

    confidence = count / len(reference_pairs) if reference_pairs else 0
    return matched_pairs, confidence


def create_json_file(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main(test_folder, reference_folder):
    test_files = [f for f in os.listdir(test_folder) if os.path.isfile(os.path.join(test_folder, f))]
    reference_files = [f for f in os.listdir(reference_folder) if os.path.isfile(os.path.join(reference_folder, f))]

    for test_file in test_files:
        test_file_path = os.path.join(test_folder, test_file)
        reference_file_path = os.path.join(reference_folder, test_file)

        if os.path.exists(reference_file_path):
            matched_pairs, confidence = compare_files(test_file_path, reference_file_path)
            json_filename = f"{test_file}_{confidence:.2f}.json"
            create_json_file(os.path.join(test_folder, json_filename), matched_pairs)
            print(f"Processed {test_file} with confidence {confidence:.2f}")
        else:
            print(f"No reference file found for {test_file}")


if __name__ == "__main__":
    test_folder = "./Nearest"
    reference_folder = "./Ground_truth"
    main(test_folder, reference_folder)