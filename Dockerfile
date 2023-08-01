FROM python:latest
RUN pip install discord openai google-api-python-client py-cord requests
RUN mkdir /opt/craig-bot/
COPY ./bot.py /opt/craig-bot/bot.py
COPY ./funcs.py /opt/craig-bot/funcs.py
COPY ./cb_classes.py /opt/craig-bot/cb_classes.py
COPY ./settings.json /opt/craig-bot/settings.json
COPY ./craig-bot.sqlite /opt/craig-bot/craig-bot.sqlite
CMD ["python","/opt/craig-bot/bot.py"]
