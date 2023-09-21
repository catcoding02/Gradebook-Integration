from github import Github
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import re
import csv

class InfoCollector():
    """
    Collects information from classroom and lab files to set class attributes
    """
    def get_instructor_info(self):
        """
        Fetches instructor access token, classroom name, JSON Access File, and Gradebook Sheet Name from Instructor_Info.csv file
        :return: github_acc_token: str:
        """
        with open("Instructor_Info.csv", newline='') as info_file:
            reader = csv.reader(info_file)
            next(reader)
            for row in reader:
                instructor_info = row
        # return instructor_info which is a list of entries from the instructor_info.csv
        return instructor_info

    def open_sheet(self, instructor_info: list):
        """
        Opens instance of Sheet from provided instructor information and JSON Key File
        :param instructor_info: list: list of instructor info extracted from Instructor_Info.csv
        :return: sheet: instance of class sheet which is the sheet the student gradebook worksheets are contained in
        """
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(f"{instructor_info[2]}",
                                                                       scopes)  # REPLACE with your JSON file!
        client = gspread.authorize(credentials)  # authenticates  the JSON key with gspread
        sheet = client.open(f"{instructor_info[3]}")
        return sheet


    def github_usernames_and_student_names(self):
        # read from csv
        """
        Generates dictionary which stores GitHub usernames as keys and Student Names as values
        :return: github_usernames_and_student_names_dict: dict: Dictionary with GitHub usernames as keys and Student Names as values
        """
        # creates empty dictionary to be appended with student info
        github_usernames_and_student_names_dict = {}
        with open("student_info.csv", newline='') as student_info_file:
            reader = csv.reader(student_info_file)
            next(reader)
            for row in reader:
                github_usernames_and_student_names_dict[row[0]] = row[1]
        return github_usernames_and_student_names_dict

    def standards_points_row(self, lab_name):
        # create empty standards + points & row dict
        spr_dict = {}
        with open(f"{lab_name}/standards_points_row.csv", newline = '') as spr_file:
            reader = csv.reader(spr_file)
            next(reader)
            # appends standards as key and point+row as key value in spr_dict
            for row in reader:
                spr_dict[row[0]] = [float(row[1]), row[2]]
        return spr_dict

    def lab_repo_and_worksheet_pair_generator(self, lab_name, git_users_stud_names: dict):
        """
        Generates dictionary. This dictionary uses the expected lab repo list. The student's lab repo name/url is the key and the
        value is the corresponding student worksheet name.
        :param lab_name: Name of lab being graded
        :param git_users_stud_names: Dictionary of student GitHub usernames and Names
        :return: lab_repo_list: list: lab repo list given lab name as student GitHub usernames
        """
        #set empty repo list
        lab_repo_and_worksheet_pair_dict = {}
        lab_repo_list = []
        worksheet_name_list = []
        def to_prefix(lab_name):
            """
            changes lab name into web prefix
            :return: lab_name: str: The lab name as a web prefix
            """
            lab_name = lab_name.lower()
            lab_name = lab_name.replace(" ", "-")
            return lab_name
        def worksheet_name(git_users_stud_names: dict):
            """
            Creates list of expected student worksheet names from provided student names
            :return: worksheet_name
            """
            for student_name in list(git_users_stud_names.values()):
                worksheet_name_list.append(f"{student_name} Gradebook")
            return worksheet_name_list
        # gets prefix from lab name provided
        prefix = to_prefix(lab_name)
        # gets list of worksheet names from list of student names provided
        worksheet_names = worksheet_name(git_users_stud_names)
        # generates expected repo list from lab prefix and provided student github usernames
        for user in list(git_users_stud_names.keys()):
            lab_repo_list.append(f"{prefix}-{user}")
        # generates dict of lab repo (key) and worksheet name (value) pairs for students
        for index,repo_name in enumerate(lab_repo_list):
            lab_repo_and_worksheet_pair_dict[lab_repo_list[index]] = worksheet_names[index]
        return lab_repo_and_worksheet_pair_dict

class CommentCollector():
    """
    Fetches and interprets comments left on GitHub and sends to a student's Google Sheets Gradebook worksheet
    """
    def validate_repo(self, ghat: str, classroom_name: str, lab_repo_and_worksheet_pair_dict: dict):
        """
        Validates that student's lab repository is present in instructor repository. Some students may sign up incorrectly, not accept an assignment, and may not
        be present in your repository list.
        """
        for lab_repo in list(lab_repo_and_worksheet_pair_dict.keys()):
            try:
                repo = Github(ghat).get_repo(f"{classroom_name}/{lab_repo}")
            except:
                # create log file?
                print(f"{lab_repo} not found!")
                # remove repo from lab_repo_worksheet_pair_dict
                del lab_repo_and_worksheet_pair_dict[lab_repo]
                continue
        # returned validated lab_repo_and_worksheet_pair_dict
        return lab_repo_and_worksheet_pair_dict

    def get_comments(self, lab_repo_and_worksheet_pair_dict_validated: dict, ghat: str, classroom_name: str, spr_dict: dict, sheet):
        """
        Fetches comments and points and sends to Google Sheets Gradebooks
        :param lab_repo_and_worksheet_pair_dict_validated: dict: A set of validated lab repo and worksheet pairs
        :param ghat: str: Instructor GitHub access token from instructor_info.csv
        :param classroom_name: str: Name of GitHub classroom in URL format from instructor_info.csv
        :param spr_dict: dict: A dictionary with the standard as the key and the list containing the points and row/number for that standard
        :param sheet: sheet: A Google Sheet that holds all of the student gradebook worksheets
        :return:
        """
        for lab_repo in list(lab_repo_and_worksheet_pair_dict_validated.keys()):
            # fetches repository for student lab so comments can be extracted
            lab_repo_object = Github(ghat).get_repo(f"{classroom_name}/{lab_repo}")
            # gets comments from repository
            lab_repo_pr = lab_repo_object.get_pulls_comments()
            # finds worksheet of student for corresponding lab_repo by accessing the value for the lab_repo key in the lab_repo_and_worksheet_pair_dict_validated dictionary
            lab_sheet = sheet.worksheet(f"{lab_repo_and_worksheet_pair_dict_validated[lab_repo]}")
            if lab_repo_pr.totalCount > 0:
                for i in lab_repo_pr:
                    standards_list = list(spr_dict.keys())
                    points_deducted_list = re.findall(": -\d+\.\d+", i.body)
                    for standard in standards_list:
                        if standard in i.body:
                            # if standard is found in the body of comment, then am able to extract the provided information about that standard
                            # from the points_row_dict to be used later
                            points_row_info = spr_dict[standard]
                            # if you wish to comment without deductions and use a standard keyword, you must type -0.0 before your comment so re.findall() does not return an error
                            points_deducted_str = points_deducted_list[0]
                            points_deducted = float(points_deducted_str.replace(": ", ""))
                            points = points_row_info[0] + points_deducted
                            # Removes standard key word so when comment is imported, it is not repeated in the student note section such as "Visualization Aesthetics: Improve data!"
                            i_cleaned_start = i.body.find(f"{standard}: ")
                            i_cleaned_end = i.body.find("\n", i_cleaned_start)
                            i_cleaned = i.body[i_cleaned_start:i_cleaned_end]
                            # remove standard points deducted so next points result can be assigned to next standard
                            points_deducted_list.pop(0)
                            # updates student gradebook worksheet, points and comment, at provided row number in standards_points_row.csv
                            lab_sheet.update_acell(f'F{points_row_info[1]}', f'{points}')
                            lab_sheet.update_acell(f'G{points_row_info[1]}', f'{i_cleaned}')
                        # addresses special case if student work receives no comments and is complete
                        elif "Complete: " in i.body:
                            i_cleaned = i.body.replace("Complete: ", "")
                            lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"RECEIVED: {i_cleaned}")
                        # addresses special case if student commits a blank lab
                        elif "Blank: " in i.body:
                            i_cleaned = i.body.replace("Blank: ", "")
                            lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"IMPORTANT: {i_cleaned}")
            # if lab_repo_pr.totalCount = 0, there are no comments to be found on a student's lab, and they must have committed nothing
            else:
                lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"IMPORTANT: No commit to comment on. Please submit lab ASAP!")


def main():
    def lab_name():
        """
        Asks user for lab name
        :return:
        """
        lab_name = input("What is the lab name? ")
        return lab_name
    IC = InfoCollector()
    CC = CommentCollector()
    lab_name = lab_name()
    info = IC.get_instructor_info()
    sheet = IC.open_sheet(info)
    ghat = info[0]
    classroom_name = info[1]
    spr_dict = IC.standards_points_row(lab_name)
    git_users_stud_names = IC.github_usernames_and_student_names()
    lab_repo_and_worksheet_pair_dict = IC.lab_repo_and_worksheet_pair_generator(lab_name, git_users_stud_names)
    lab_repo_and_worksheet_pair_dict_val = CC.validate_repo(ghat, classroom_name, lab_repo_and_worksheet_pair_dict)
    CC.get_comments(lab_repo_and_worksheet_pair_dict_val, ghat, classroom_name, spr_dict, sheet)


