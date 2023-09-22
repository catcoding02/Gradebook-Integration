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

**COME BACK TO THIS STEP AFTER SETTING UP YOUR GOOGLE SHEETS GRADEBOOK** 
As you can see from the template Gradebook provided in the guide, different assignments have information stored in different rows under the different standards. In the third column of this CSV file, paste the row that corresponds to the information for the standard for this assignment in a student's Google Sheets Gradebook.

## Setting Up Your Google Sheets Gradebook
Follow [this link](https://medium.com/@lledwards/google-sheets-gradebook-guide-integrating-github-google-sheets-and-slack-cf70b109f3db) to my Medium article that details how to set up a Google Sheets Gradebook that can interact with this program. Templates and examples are provided.
 
# Sources
Credit to [Ben Collins](https://www.benlcollins.com/spreadsheets/marking-template/) for providing guidance on Slack integration with Google Sheets in a gradebook context.
