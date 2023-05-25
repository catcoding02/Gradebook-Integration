This project aims to streamline the process of submitting code reviews in GitHubClassroom and entering points earned into student gradebooks in Google Sheets, as well as updating students on their assignment grades via Slack. To make use of this in your classroom, you will need to first input the GitHub usernames and names of your students in `student_info.csv`. You will also need to provide the standards your course is graded on in `standards.csv`. Then, leave comments as normal on your students' work. See the included example gradebook for tips on formatting to make this program and scripts run smoothly. Note that this program detects comments on standards and points-earned based on keywords, so a comment should be prefixed by &lt;YOUR STANDARD NAME HERE>. Add any points deducted immediately after the standard keyword. 

# Comment Format
A properly-formatted comment looks like: 
  
  *Addition: -0.9 Great job, but next time, add all of the values together.*
  
In the above example, the student is being graded on the `Addition` standard, and had -0.9 points deducted from the standard for their mistake. 

# Sources
Credit to [Ben Collins](https://www.benlcollins.com/spreadsheets/marking-template/) for providing guidance on Slack integration with Google Sheets in a gradebook context.
