import yaml
import os


def load_config(file_path):
    with open(file_path, 'r', encoding= "utf-8") as file:
        return yaml.safe_load(file)


def get_work_path():
    current_file_path = os.path.abspath(__file__)
    project_root_directory = os.path.dirname(current_file_path)
    project_root_directory = os.path.dirname(os.path.dirname(current_file_path))

    return project_root_directory + os.sep






if __name__ == '__main__':
    print(get_work_path())