import funcs, openai, re
settings = funcs.get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
openai_token = settings['openai']['token']
db_file = settings['bot']['db_file']

openai.api_key= openai_token
model = "gpt-3.5-turbo"
data = [
            {"role": "assistant", "content": "limit the response to 200 characters or less"},
            {"role": "user", "content": "tell me about python"}
        ]
response = openai.ChatCompletion.create( # Change this
        model = model, # Change this
        messages = data,
        max_tokens = 256,
        n = 1,
        stop = None,
        temperature = 0.5,
        )
print(response)

# users = ["<@49832143829> other text","<@89438924> this would be a message","<@324132193102> i like turtles", "no user id here", "<@9302139201> another message"]
# strip_user_regex=re.compile('\<[^)]*\>')
# for u in users:
#     try:
#         print( funcs._strip_user_id( u ) )
#     except Exception as e:
#         print( u )
#         continue

# output = []
# for u in users:
#     print(strip_user_regex.match(u))
#     output.append(u[strip_user_regex.match(u).end()+1:len(u)])
# print(output)