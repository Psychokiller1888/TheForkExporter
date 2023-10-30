# TheForkExporter
Export your customer data without subscription to shameless prices

## Howto
- **Turn off your computer sleep mode and auto logout after time inactivity!!**
- Install Git: https://git-scm.com/downloads
- Install Python: https://www.python.org/downloads/
- Clone and install this repo:
- - Open a terminal
- - Type the following in you terminal:
```
git clone https://github.com/Psychokiller1888/TheForkExporter.git
cd TheForkExporter
pip install -r requirements.txt
```
- Now that we have installed what's needed, you need to get some information about your TheFork account. Leave the terminal open and open your web browser
- - Browse to your account: https://manager.thefork.com and login to your account
- - Once logged in, press `F12` which should open the browser dev console either on the bottom of the page or on it's side
- - Go to the `Network tab` in the dev console
- - Press `F5` which will trigger a page reload and populate the `Network` tab with lots of stuff
- - Under `Name` look for one, best is the second one in the list, called `graphql` and click on it
- - In the middle of the dev console, on the `Headers`tab, look for `Query headers` and expend it
- - Look for `Authorization` and copy the gigantic text after `Bearer`, this is your **authorization token**
- - **!! DO NEVER EVER SHARE THIS TOKEN !! Even if asked so by me, The Fork, the Microsoft support with the weird Indian accent, or your dad/mom, President, King, Queen whoever**
- - In the middle of the dev console, on the `Payload` tab expend everything, until you see something like `variables: {restaurantUuid: "asdsdsed-sdsd-sdsd-dsds-dsdsdsdsdasddsd"}`
- - Copy that weird text, without the double quotes, the `asdsdsed-sdsd-sdsd-dsds-dsdsdsdsdasddsd` similar part. This is your **uuid**
- Now that we have what we need, let's make the script work and get you your data!
- Return to the terminal and type
- - `python main.py --id="REPLACE WITH YOUR UUID" --token="REPLACE WITH YOUR TOKEN"`
- - **NOTE** replace the required parts with your uuid and token and make sure to leave the double quotes around them
- - Press enter to start the process.
- - Leave the terminal working by itself, it will spit out information about what it is doing
- - - If you get authorization errors, either your token or uuid is wrong

Fetching the customers list takes a while as TheFork doesn't provide an easy way to fetch more than 10'000 customers. You should get about 20'000 customer ids in under 15 minutes. But fetching the customers data is a very long process. And when I say very long, I mean it. Fetching data for 1000 customers can take 15 minutes, so be prepared.

Even with that long process, you cannot be sure that all your customers will be exported, this is very important to understand. For techs, the reason why is that TheFork doesn't let you use any mass export API unless you spit out an insane amount of money monthly to access the customer database part. So we are left with using the search function, but they are using graphql scheme without pagination and have locked the max amount of accessible data to 10'000. The reason why you are able to access more than 10'000 customers is that by manipulating the query and applying different sorting directions, you get a different list of 10'000 customers. There are 9 possible sorting possibilities, not all offered by the website, but supported by their graphql backend. By reasoning correctly, you should at least get the 10k last customers, 10k first customers, first 10k first name alpha up customers, first 10k first name alpha down customers, first 10k mixed customers etc which should cover a lot of them.

## Where are my customers after the export completed?

They are in a database created locally on your computer when you started this script. If you want to access it, contact me and spit out money!

Nope... joking... about the money part of course. The database is in the directory you cloned, by default `"C:\TheForkExporter"` in a file name `database.sqlite`.

**DON'T EVER SHARE THIS FILE!!! Even if blablabla, you know the drill...** It contains all your customer private information and sharing that is a violation of their privacy and the laws protecting these data, such as the GDPR (EU), nLPD (Switzerland) etc etc

You can open a SQLite database with a small program such as `SQLite browser`: https://sqlitebrowser.org. Download it, install it and point it to the above mentioned file. You can use SQLite browser to export the data to .csv for Microsoft Excel per example.

## Going further

Once the list of customer was fetched, their id is stored, but the data is not yet downloaded, which means you can easily restart the operation by using `--resume=true` in the command line. If for any reason you want to start fresh, use the `--fresh=true` option in the command line.

Another data of value we can get is the reservation history. For that, start the script with the argument `--history`. Same story, this will take a long time... A veeeery long time.... It took long to get all the customers, now if all your customers are returning customers, they have many reservations to download, it's... exponential... 