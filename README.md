# Bot Against Humanity
[![Build Status](https://travis-ci.org/ErikBoesen/BotAgainstHumanity.svg?branch=master)](https://travis-ci.org/ErikBoesen/BotAgainstHumanity)

> Bot Against Humanity allows members of GroupMe chats to virtually play everyone's favorite party game for terrible people.

![Screenshot](screenshot.png)

## Motivation
Bot Against Humanity was created by [Erik Boesen](https://github.com/ErikBoesen). It grew out of [Yalebot](https://github.com/ErikBoesen/Yalebot), a bot designed (also by Erik) for Yale University's Class of 2023 GroupMe chats. Yalebot is a very complex bot with several hundred different functions, of which facilitating virtual Cards Against Humanity games was only one. The card game did not fit well into the existing modular infrastructure of Yalebot due to the need for interaction through the chat, a web interface, and websockets. As such, Yalebot's CAH functionality was spun off into this bot.

To add this bot to your own server, go [here](https://botagainsthumanitygroupme.herokuapp.com)!

## Platform
Bot Against Humanity runs best on [Heroku](https://heroku.com). Simply push the code via Heroku CLI and the bot will launch.

## License
[GPL](LICENSE)
