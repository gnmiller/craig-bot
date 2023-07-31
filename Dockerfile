FROM python:latest
RUN pip install discord openai google-api-python-client py-cord requests
RUN mkdir /opt/craig-bot/
RUN apt install git -y
RUN git config --global --add safe.directory /opt/craig-bot/
RUN git clone https://github.com/gnmiller/craig-bot.git /opt/craig-bot
COPY ./settings.json /opt/craig-bot/settings.json
COPY ./craig-bot.sqlite /opt/craig-bot/craig-bot.sqlite
RUN cd /opt/craig-bot/
CMD ["sh"]
