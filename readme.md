# Velozone
## Velozone Usage
Velozone is a costum developed webapp which allows the Wielercenter Eddy Merckx in Ghent to host trackcycling sessions with a realtime updating leaderboard and the ability to generate PDF reports containing the session data.

### Name Configuration
Click the `Name Configuration` button to get to the 'Name Configuration' webpage. This webpage will present you with a form in which the users can connect their transponder IDs to their names. There is also a table present with the already configured names.

### Start Session
Click the `Start Session` button to begin a new session. This will present you with a 'Leaderbord Configuration' webpage which contains a form in which one configures:
- Start Date
- Start Time
- Competition Duration
- Number of Participants

Once this configuration is submitted through the `Start Competition` button, the session will be started and one can choose to either go back to the home page through the `Go to Home` button or to view the leaderboard through the `Go to Leaderboard` button.

Starting the session also starts a visual indicator which shows that the session is active. This indicator is a green square in the top right corner with a rotating animation. If the session is not active, the indicator is a grey static square.

### Leaderbord
Once a session is started, the leaderbord can be displayed either by clicking the `Go to Leaderboard` button after configuring the session or by clicking the `Leaderboard` button on the home page.

The Leaderbord contains the next information:
- Average laptimes
- Top 5 fastest laps
- Slowest lap (badman)
- Most consistent-paced rider (diesel engine)
- Rider with the highest acceleration (electric motor)

The leaderboard is updated every 3 seconds.

### Stop Session
(nog bekijken om juist te beschrijven/aan te passen met de beschrijving)

When the `Stop Session` button on the main page is clicked, you will be asked if you want a PDF generated. If one chooses 'yes', a PDF will be generated and the session will be stopped. If one chooses 'no', the session will be stopped and the leaderboard will be closed. (**?**)

### Generate Report
The `Generate Report` button on the main page will generate a PDF report of the data that has been collected during the session.

## Installation
(pip) Install the required packages available in [requirements.txt](requirements.txt)

## Usage
Run the following command in the terminal. This starts a webpage via http://127.0.0.1:5000, which is a development server.

    python app.py

## Deployment
De app runs via Vercel. You can acces it via [https://velozone.vercel.app/](https://velozone.vercel.app/).


## Github usage
### Pulling Code
To get the latest code from github, run the following command:

    git pull

### Pushing Code
After making changes to the code, you can commit the changes. A commit makes a local 'checkpoint':

    git add .
    git commit -m 'some message'

When a commit is made, it is still in your local repository. You don't necessarily need to perform a push after each commit. You can either choose to keep on coding or to push the commit to the remote repository (on github).

To push the code:

    git push
