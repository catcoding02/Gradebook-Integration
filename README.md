# Purpose
This project aims to streamline the process of submitting code reviews in GitHubClassroom and entering points earned into student gradebooks into Google Sheets, as well as updating students on their assignment grades via Slack. 

# Setting Up Your Space
To make use of this in your classroom, you need to fill in some of the blank CSV files with your and your students' information. The following sections will provide directions for filling out and/or generating the set-up files and what they are used for in the program.

## JSON Access File
Before you set up anything else, you will have to set up a service account to allow Python to communicate with the Google Sheets API and your Google account. Here are the directions, taken from the gspread documentation linked [here](https://docs.gspread.org/en/v5.1.0/oauth2.html#enable-api-access-for-a-project). 

> A service account is a special type of Google account intended to represent a non-human user that needs to authenticate and be authorized to access data in Google APIs. 
> 1.  [Enable API Access for a Project](https://docs.gspread.org/en/v5.1.0/oauth2.html#enable-api-access)  if you haven’t done it yet.
> 2. Go to “APIs & Services > Credentials” and choose “Create credentials > Service account key”.
> 3. Fill out the form
> 4. Click “Create” and “Done”.
> 5. Press “Manage service accounts” above Service Accounts.
> 6.  Press on  **⋮**  near recently created service account and select “Manage keys” and then click on “ADD KEY > Create new key”.
> 7.  Select JSON key type and press “Create”. You will automatically download a JSON file with credentials. You’ll need the value of _client_email_ from this file for Step 8.
> 8. **VERY IMPORTANT!** Go to your spreadsheet and share it with a  _client_email_  from the step above, just like you do with any other Google account. If you don’t do this, you’ll get a  `gspread.exceptions.SpreadsheetNotFound`  exception when trying to access this spreadsheet from your application or a script. Since it’s a separate account, by default it does not have access to any spreadsheet until you share it with this account. Just like any other Google account.>
> 9. Now, move your JSON file to the same directory of the Python program. Name it something that makes sense, like `stats-classroom.json` or `fall23_physics.json`. 

## instructor_info.csv
You will see you have downloaded a blank CSV called `instructor_info.csv`. 

**In the first column, `Github_Access_Token`, of this CSV file, you will paste your GitHub Access Token.** Instructions for the creation of a GitHub Access Token can be found [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). This access token allows the program access to your GitHub account and all of the repositories you have access to. 

**In the second column, `Classroom_Name`, of this CSV file, you will paste your classroom's name.** Go into GitHub Classroom and click on your classroom. On the top of the page, you will see something like the following image:
![Example of GitHub Classroom Title](https://imgur.com/a/0UAkNTa)
Notice the smaller, grey text below the bold Classroom Title, `sds192fall2023` in this example. **THIS** text is your classroom's name, which you will paste in the second column of the CSV file. 

**In the third column, `JSON_Access_File`, of this CSV file, you will paste the name of the JSON Access file you created and put into your directory.** So, if the name of your JSON Access file is `stats-classroom.json`, you would paste `stats-classroom`. 

**In the fourth column, `Gradebook_Sheet_Name`, of this CSV file, you will paste the name of the Google Sheets file that holds your all of your gradelogs and student gradebooks.** If the name of this file contains spaces, please retain them as-is.

## student_info.csv
You will see you have downloaded a blank CSV called `student_info.csv`. 

**In the first column, `GitHub Username`, paste a student's GitHub username.**

**In the second column, `Student Name`, paste a student's name.** This name should match the name of their gradebook in Google Sheets. For example, if a student's gradebook in Google Sheets is `John Smith Gradebook`, the name you should paste in this column is `John Smith`. **IMPORTANT** Each student's gradebook should be named in the format "`<name>` Gradebook." Setting up your Google Sheets file is covered in-detail in my Medium article linked [here](https://medium.com/@lledwards/google-sheets-gradebook-guide-integrating-github-google-sheets-and-slack-cf70b109f3db). 

## standards_points_row.csv
For each assignment you assign your students, you will create a new `standards_points_row.csv` file. A template is provided for you. For each assignment, in the same directory that contains the code for the program, create a new folder on your local machine that shares the same name of the assignment name on GitHub Classroom. So, if the assignment on GitHub Classroom is called `Lab1`, create a folder called `Lab1`.  Then, create a new CSV file called `standards_points_row.csv` in this folder. You must do this for **EVERY** individual assignment. 

**In the first column of this CSV file, paste a standard that this assignment is evaluating.**

**In the second column of this CSV file, paste the number of points that a student can earn on this standard for this assignment.**

**!COME BACK TO THIS STEP AFTER SETTING UP YOUR GOOGLE SHEETS GRADEBOOK!** 
As you can see from the template Gradebook provided in the guide, different assignments have information stored in different rows under the different standards. **In the third column of this CSV file, paste the row that corresponds to the information for the standard for this assignment in a student's Google Sheets Gradebook.**

## Setting Up Your Google Sheets Gradebook
Follow [this link](https://medium.com/@lledwards/google-sheets-gradebook-guide-integrating-github-google-sheets-and-slack-cf70b109f3db) to my Medium article that details how to set up a Google Sheets Gradebook that can interact with this program and Slack, if you wish. Templates and examples are provided.

# Running the Program
If you have set everything up correctly, running the program is easy! You will be prompted to enter the assignment name upon running. Be sure to enter the name of the assignment exactly as it is named in GitHub classroom, which is also the same name of the folder containing the `standards_points_row.csv`. 

The program will print a statement, but not stop, if a student's lab repository is not found in your accessible repositories. This occurs if a student does not accept an assignment or has incorrectly joined your classroom. 

The below section will go into detail about how to format your comments on GitHub so the program can detect any deductions on standards that you have indicated in your summary comment on a student's assignment:

## Guide to Proper GitHub Comments

The Python Program utilizes keywords in order to detect when a student has lost points on a standard. These standards come from the standards stored in the first column of your assignment's `standards_points_row.csv` file. It is best practice to leave ONE comment at the end of a student's lab that contains overall comments and points lost for all relevant standards. Only include standards where points have been lost in this overall comment. 

The comment should be formatted as follows:

"[standard1]: -[number] /<comment/>

[standard2]: -[number] /<comment/>

[standard3]: -[number] /<comment/>

[standard4]: -[number] /<comment/>"


**IMPORTANT**

> You must type a standard EXACTLY (capitalization, spaces, etc.) as you have typed it in your `standards_points_row.csv` file.

> You must also indicate the points lost in the format <number>.<number>, with a decimal place! So if a student has lost 2 points, you must write "-2.0", not "-2". 

For example, if a student has lost 0.9 points on the 'Mapping' standard, lost 0.3 on the 'Visualization Context' standard, and -1.0 points on the "Data Ethics" standard, there must be only ONE comment on their GitHub feedback which is formatted as follows:

"Mapping: -0.9. You need to improve your mapping skills.
Visualization Context: -0.3 Please improve the colors on your graphs.
Data Ethics: -1.0 You did not answer the question for this standard in Example 9."

Note that other comments can be left, as long as they do not include the "[standard1]: -[number]" format. Again, best practice would be that once comments have been left on a lab's contents, ONE overall comment should be left for relevant standards at the end of the lab so the overall points lost per standard can be recorded. 

Let's say a student has incorrect mapping techniques at Lines 9, 20, and 120 on a lab. You can leave comments at all of these lines of code correcting the student, such as "This map has the wrong color!" Or "This map should be zoomed in more." Then, at the end of the lab, your one overall comment for the Mapping standard would be something such as:

"Mapping: -0.4. Please address the comments about your maps left in Line 9, 20, and 120."

# Conclusion

This concludes the README file for the program. If you have any questions, please reach out to lledwards@smith.edu. Thank you!




 
# Sources
Credit to [Ben Collins](https://www.benlcollins.com/spreadsheets/marking-template/) for providing guidance on Slack integration with Google Sheets in a gradebook context.
