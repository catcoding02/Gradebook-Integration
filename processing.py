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
        sheet = client.open("SDS192 Gradebooks")
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

    def mp_group_names_and_student_names(self, assignment_name: str):
        # read from csv
        """
        Generates dictionary which stores MP group names as keys and group Student Names as values
        :return: mp_group_names_and_student_names_dict: dict: Dictionary with MP group names as keys and group Student Names as values
        """
        # creates empty dictionary to be appended with student info
        mp_group_names_and_student_names_dict = {}
        with open(f"{assignment_name}/{assignment_name}_group_info.csv", newline='') as mp_info_file:
            reader = csv.reader(mp_info_file)
            next(reader)
            for row in reader:
                # must format multi-student groups as list in row such as ["John Smith", "Ken Banks"]
                group_list = []
                # assumes groups get no bigger than 10 people
                for i in range(1,11):
                    try:
                        len(row[i])
                        group_list.append(row[i])
                        continue
                    except:
                        break
                mp_group_names_and_student_names_dict[row[0]] = group_list
        print(mp_group_names_and_student_names_dict)
        return mp_group_names_and_student_names_dict

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

    def assignment_repo_and_worksheet_pair_generator(self, assignment_name, repos_and_stud_names: dict):
        """
        Generates dictionary. This dictionary uses the expected lab repo list. The student's lab repo name/url is the key and the
        value is the corresponding student worksheet name.
        :param assignment_name: Name of lab being graded
        :param repos_and_stud_names: Dictionary of student GitHub usernames and Names
        :return: assignment_repo_and_worksheet_pair_dict: dict: assignment repo  given lab name as student GitHub usernames
        """
        # set empty repo list
        assignment_repo_and_worksheet_pair_dict = {}
        assignment_repo_list = []
        worksheet_name_list = []
        def to_prefix(assignment_name):
            """
            changes assignment name into web prefix
            :return: assignment_name: str: The lab name as a web prefix
            """
            assignment_name = assignment_name.lower()
            assignment_name = assignment_name.replace(" ", "-")
            return assignment_name

        def worksheet_name(repos_and_stud_names: dict):
            """
            Creates list of expected student worksheet names from provided student names
            :return: worksheet_name
            """
            # student_item may be individual student or groups of students
            for student_item in list(repos_and_stud_names.values()):
                if len(student_item) == 1:
                    worksheet_name_list.append(f"{student_item} Gradebook")
                elif len(student_item) > 1:
                    for index, student in enumerate(student_item):
                        student_item[index] = f"{student} Gradebook"
                    worksheet_name_list.append(student_item)
            return worksheet_name_list
        # gets prefix from lab name provided
        prefix = to_prefix(assignment_name)
        # gets list of worksheet names from list of student names provided
        worksheet_names = worksheet_name(repos_and_stud_names)
        # generates expected repo list from lab prefix and provided student github usernames
        for item in list(repos_and_stud_names.keys()):
            assignment_repo_list.append(f"{prefix}-{item}")
        # generates dict of lab repo (key) and worksheet name (value) pairs for students
        for index,repo_name in enumerate(assignment_repo_list):
            assignment_repo_and_worksheet_pair_dict[assignment_repo_list[index]] = worksheet_names[index]
        print(assignment_repo_and_worksheet_pair_dict)
        return assignment_repo_and_worksheet_pair_dict

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
        print(lab_repo_and_worksheet_pair_dict)
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
                            # clears any previous special case comments
                            lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', "")
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
                            print(i_cleaned)
                            lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"RECEIVED: {i_cleaned}")
                        # addresses special case if student commits a blank lab
                        elif "Blank: " in i.body:
                            i_cleaned = i.body.replace("Blank: ", "")
                            lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"IMPORTANT: {i_cleaned}")
            # if lab_repo_pr.totalCount = 0, there are no comments to be found on a student's lab, and they must have committed nothing
            else:
                lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"IMPORTANT: No commit to comment on. Please submit lab ASAP!")

    def get_mp_comments(self, lab_repo_and_worksheet_pair_dict_validated: dict, ghat: str, classroom_name: str, spr_dict: dict, sheet):
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
            print(lab_repo)
            # fetches repository for MP group so comments can be extracted
            lab_repo_object = Github(ghat).get_repo(f"{classroom_name}/{lab_repo}")
            # gets comments from repository
            lab_repo_pr = lab_repo_object.get_pulls_comments()
            # finds worksheet of students for corresponding mp_repo by accessing the value for the lab_repo key in the lab_repo_and_worksheet_pair_dict_validated dictionary
            for student in lab_repo_and_worksheet_pair_dict_validated[lab_repo]:
                lab_sheet = sheet.worksheet(f"{student}")
                if lab_repo_pr.totalCount > 0:
                    for i in lab_repo_pr:
                        standards_list = list(spr_dict.keys())
                        points_deducted_list = re.findall(": -\d+\.\d+", i.body)
                        for standard in standards_list:
                            if standard in i.body:
                                # clears any previous special case comments
                                lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', "")
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
                                print(i_cleaned)
                                lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"RECEIVED: {i_cleaned}")
                            # addresses special case if student commits a blank lab
                            elif "Blank: " in i.body:
                                i_cleaned = i.body.replace("Blank: ", "")
                                lab_sheet.update_acell(f'G{spr_dict["Special"][1]}', f"IMPORTANT: {i_cleaned}")
                # if lab_repo_pr.totalCount = 0, there are no comments to be found on a student's lab, and they must have committed nothing
                else:
                    lab_sheet.update_acell(f'G{spr_dict["Special"][1]}',
                                           f"IMPORTANT: No commit to comment on. Please submit lab ASAP!")



def main():
    def mini_project():
        """
        Asks user if assignment is mini project or not
        :return: str: Y or N for if mini project or not
        """
        mp_status = input("Is this assignment a mini-project? Answer Y/N: ")
        return mp_status
    def assignment_name():
        """
        Asks user for assignment name
        :return:
        """
        assignment_name = input("What is the assignment name? ")
        return assignment_name
    IC = InfoCollector()
    CC = CommentCollector()
    mp_status = mini_project()
    assignment_name = assignment_name()
    info = IC.get_instructor_info()
    sheet = IC.open_sheet(info)
    ghat = info[0]
    classroom_name = info[1]
    spr_dict = IC.standards_points_row(assignment_name)
    if mp_status == "Y":
        repos_and_stud_names = IC.mp_group_names_and_student_names(assignment_name)
    elif mp_status == "N":
        repos_and_stud_names = IC.github_usernames_and_student_names()
    assignment_repo_and_worksheet_pair_dict = IC.assignment_repo_and_worksheet_pair_generator(assignment_name, repos_and_stud_names)
    assignment_repo_and_worksheet_pair_dict_val = CC.validate_repo(ghat, classroom_name, assignment_repo_and_worksheet_pair_dict)
    CC.get_comments(lab_repo_and_worksheet_pair_dict_val, ghat, classroom_name, spr_dict, sheet)



