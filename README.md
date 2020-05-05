# [MeBots](http://mebots.co)
[![Build Status](https://travis-ci.org/ErikBoesen/MeBots.svg?branch=master)](https://travis-ci.org/ErikBoesen/MeBots)

> A simple API framework for managing large-scale GroupMe bots.

![Banner](app/static/images/logo/banner.png)

## Motivation
GroupMe's bot framework has no native support for third-party adding of bots to servers. Since GroupMe requires the creation of a bot within a single group and essentially mandates mapping group IDs to bot IDs in order for a bot to function across multiple servers, the only option for scalable and open adding of the bot without owner oversight was previously to roll your own database system and custom web interface to allow users to log in through the GroupMe API and use a user's token to add the bot, then store the bot's ID and recall it when receiving a message. This process is similar between different bots, which can result in a lot of nasty code reuse.

MeBots handles the entire bot lifecycle process and extends it beyond what GroupMe normally supports. Bot developers can provide basic details about their bot, and other users can find bots and easily add them to their own chats with just a few clicks. MeBots communicates with GroupMe's API behind the scenes to create different bot instances and store away relevant data. Then, when a bot receives a message, a bot program can query MeBots' API and ask where to send a response.

Read more about MeBots' goals and implementation [here](http://mebots.co/about), and read the documentation [here](http://mebots.co/documentation)!

## Platform
MeBots runs on [Heroku](https://heroku.com). It is build upon Flask and uses PostgreSQL for database management.

## Author
[Erik Boesen](https://github.com/ErikBoesen)

## License
[GPL](LICENSE)
