import os
import csv

def dump_runner_output_to_csv(results, filepath):
    if os.path.exists(filepath):
        raise ValueError("Output file path already exists")

    with open(filepath, "w", newline='') as filehandler:
        csv_writer = csv.writer(filehandler)
        csv_writer.writerow(["Candidate evidence id", "Relation present"])
        for prediction, value in results.items():
            prediction_id = prediction.id
            csv_writer.writerow([prediction_id, value])


def dump_output_loop(predictions):
    while True:
        output_filepath = input("\nChoose the filename of the output (in csv format): ")
        try:
            dump_runner_output_to_csv(predictions, output_filepath)
            break
        except ValueError:
            print("Error: file already exists, try another one.\n")
