# GroupMeBot
[![Build Status](https://travis-ci.org/ErikBoesen/GroupMeBot.svg?branch=master)](https://travis-ci.org/ErikBoesen/GroupMeBot)

> A simple API framework for managing large-scale GroupMe bots.

## Motivation
GroupMe's bot framework has no native support for third-party adding of bots to servers. Since GroupMe requires the creation of a bot within a single group and essentially mandates mapping group IDs to bot IDs in order for a bot to function across multiple servers, the only option for scalable and open adding of the bot without owner oversight was previously to roll your own database system and custom interface to allow users to log in through the GroupMe API and use a user's token to add the bot, then store the bot's ID. This process is similar between bots and is tedious to develop and configure. So, GroupMeBot abstracts away this  process,

## Platform
GroupMeBot runs on [Heroku](https://heroku.com).

## License
[GPL](LICENSE)
