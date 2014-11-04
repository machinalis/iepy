import os
import csv
import pickle


def dump_runner_output_to_csv(results, filepath):
    """
    Takes the result of a runner and dumps it into a csv file with the
    following format:

    <candidate_evidence_id>,<relation_is_present_boolean>
    """

    if os.path.exists(filepath):
        raise ValueError("Output file path already exists")

    with open(filepath, "w", newline='') as filehandler:
        csv_writer = csv.writer(filehandler)
        csv_writer.writerow(["Candidate evidence id", "Relation present"])
        for prediction, value in results.items():
            prediction_id = prediction.id
            csv_writer.writerow([prediction_id, value])


def dump_classifier(extractor, filepath):
    """
    Takes an extractor and stores the classifier into filepath.
    """

    if os.path.exists(filepath):
        raise ValueError("Output file path already exists")

    with open(filepath, 'wb') as filehandler:
        pickle.dump(extractor.relation_classifier, filehandler)


def load_classifier(filepath):
    """
    Takes an extractor and stores the classifier into filepath.
    """

    if not os.path.exists(filepath):
        raise ValueError("File does not exists")

    with open(filepath, 'rb') as filehandler:
        return pickle.load(filehandler)


def dump_output_loop(predictions):
    """
    Ask the user the filepat to store the runner's result.
    If the file already exists keeps asking until it gets an answer
    """

    while True:
        output_filepath = input("\nChoose the filename of the output (in csv format): ")
        try:
            dump_runner_output_to_csv(predictions, output_filepath)
            break
        except ValueError:
            print("Error: file already exists, try another one.\n")
        except FileNotFoundError:
            print("Error: couldn't open the file, try another one.\n")


def dump_classifier_loop(extractor):
    """
    Ask the user if he wants to save the classifier, and in that case where.
    If the file already exists keeps asking until it gets an answer
    """

    while True:
        answer = input("\nDo you want to save the classifier generated? (y/n): ")
        if answer not in ["y", "n", "yes", "no"]:
            print("Invalid answer\n")
        else:
            break

    if answer in ["y", "yes"]:
        while True:
            output_filepath = input("\nChoose the filename of the output: ")
            try:
                dump_classifier(extractor, output_filepath)
                break
            except ValueError:
                print("Error: file already exists, try another one.\n")
            except FileNotFoundError:
                print("Error: couldn't open the file, try another one.\n")


