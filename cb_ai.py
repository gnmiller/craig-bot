from discord.ext import commands
import funcs
import openai


class cb_ai(commands.Cog, name="OpenAI"):
    def __init__(self, bot, openai_api_key):
        self.bot = bot
        self.openai_token = openai_api_key

    def prompt_openai(self, in_text, user, openai_key,
                      model="gpt-3.5-turbo",
                      max_resp_len=200,
                      db_file="craig-bot.sqlite"):
        """Interact with OpenAI's API."""
        try:  # if no id in message pass the raw message as input to chatgpt
            prompt = funcs.strip_user_id(in_text)
        except RuntimeError:
            prompt = in_text
        try:
            openai.api_key = openai_key
            data = [
                {"role": "assistant", "content": "limit the response to {} characters or less".format(max_resp_len)},
                {"role": "user", "content": "{}".format(prompt)}
            ]
            response = openai.ChatCompletion.create(
                                                    model=model,
                                                    messages=data,
                                                    max_tokens=256,
                                                    n=1,
                                                    stop=None,
                                                    temperature=0.5,
            )
            self._log_ai_prompt(in_text, model, response,
                                user.id, db_file, funcs.now())
            return response
        except openai.error.InvalidRequestError as e:
            print(e)
            return None

    def _log_ai_prompt(in_text, model, reply, user, db_file="craig-bot.sqlite", date=funcs.now()):
        # TODO implement this in the process for returning AI prompts
        db_data = {
                "prompt": in_text,
                "model": model,
                "resp": reply,
                "uid": user,
                "date": date,
            }
        try:
            db = funcs._check_db(db_file)
            cur = db.cursor()
            q = "INSERT INTO oai_cmds VALUES(\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
                db_data["prompt"],
                db_data["model"],
                db_data["resp"],
                db_data['uid'],
                db_data["date"])
            res = cur.execute(q)
            db.commit()
            db.close()
            return res
        except Exception:
            db.rollback()
            db.close()
            return None

    @commands.command(
            help="Prompt OpenAI for a response. A response limit can be specified."
                 " If none is given the bot will assume 200 or less characters in"
                 " the response to help avoid API limits. There is a hard cap of"
                 " 1024 characters on any response.\n",
            brief="Prompt OpenAI. This command is also available via @mention.",
            usage="!openai [len=prompt_max_length] [model=openai_model] <prompt text>",
    )
    async def openai(self, ctx, model, *, message):
        def_length = 200
        def_model = "gpt-3.5-turbo"
        index = 0
        length = def_length
        model = def_model
        temp = ""

        # check for params
        for i in message.split():
            if i.startswith("len") and length == def_length:
                try:
                    length = i.split('=')[1]
                    index += 1
                except Exception:
                    length = def_length
            if i.startswith("model") and model == def_model:
                try:
                    model = i.split('=')[1]
                    index += 1
                except Exception:
                    model = def_model
    
        # set the prompt string
        for i in message.split()[index:]:
            temp += i+" "
        prompt = temp[0:len(temp)-1]

        # commune with the elders
        msg_to_edit = await ctx.send("```Please hold while I commune with SkyNet.```")
        oai_resp = funcs.prompt_openai(in_text=prompt, user=ctx.author,
                                       openai_key=self.openai_token, model=model,
                                       max_resp_len=length, db_file=self.db_file)
        await msg_to_edit.edit(content="```"+str(oai_resp.choices[0].message.content+"```"))
        return None
