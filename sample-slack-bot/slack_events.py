from flask import Flask
from slack_configure import slack_configure
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import elastic_search
import json
import threading
import queue

app = Flask(__name__)

slack_bot_token, slack_bot_secrete = slack_configure().return_slack_config()

print(slack_bot_token)
print(slack_bot_secrete)

slack_client = WebClient(slack_bot_token)
slack_event_adapter  = SlackEventAdapter(slack_bot_secrete,'/slack/events',app)

q = queue.Queue()



@slack_event_adapter.on("app_mention")
def handle_message(event_data):
    print("..........................................................")

    threading.Thread(target=process_message).start()
    q.put(event_data)

    return "HTTP 200 OK"



#    msg= event_data
#    print(msg)
#    blocks = (msg.get('event').get('blocks'))
#    user_id = (blocks[-1].get('elements')[-1].get('elements')[0].get('user_id'))
#    user = msg.get('event').get('user')
#
#    channel = msg.get('event').get('channel')
#    print("******")
#    print(channel)
#    print("*******")
#    thread_id = msg.get('event').get('ts')
#    text = (blocks[-1].get('elements')[-1].get('elements')[1].get('text'))
#
#    if text.replace(" ","") == 'help':
#        slack_client.chat_postMessage(channel=channel,
#                                  thread_ts=thread_id,
#                                  text="""<@"""+user+""">  Following commands are supported...
#                                  \n #. 1. download logs from <environment name> from device <device name> with search string <search string> from time <from time ust> to <to time ust>
#                                  \n #. 2. download logs from <evnironment name> from device <device name> from time <from time ust> to <to time ust>
#                                  \n #. 3. downloads logs from <environment name> from microservice with search string <search string> from time <from time ust> to <to time ust>)
#                                  \n #. 4. download logs from <environment name> from microservcice <service name> with search string <search string> from time <from time ust> to <to time ust>
#                                  \n #. 5. downloads logs from <environment name> from microservice from time <from time ust> to <to time ust>
#                                  \n #. 6. download logs from <environment name> from microservcice <service name> from time <from time ust> to <to time ust>
#                                  \n #. 7. Note : Use capital 'AND' or 'OR' if you want to include 'AND' or 'OR' in search string
#                                  \n #. 8. Format for time : from time : 2022-07-08T07:30:00.000Z to time: 2022-07-08T10:00:00.000Z """)
#
#    elif 'download' in text:
#        result = slack_client.chat_postMessage(channel=channel,
#                                  thread_ts=thread_id,
#                                  text="<@"+user+">  Request started. Will update once completed")
#
#
#        print(result)
#
#        logs = elastic_search.parse_command(text)
#
#        #print(type(logs))
#
#        #print("*****")
#        #print(logs)
#
#        with open('/home/pocuser/ZedBot/logs.txt', 'w') as f:
#            f.write(logs)
#
#
#        print("uploaidn gthe logs..")
#
#        result =  slack_client.files_upload(channels=channel,
#                                  filename='logs.txt',
#                                  title = 'Logs..',
#                                  filetype= 'text',
#                                  file = '/home/pocuser//logs.txt')
#
#        print(result)
#
#        print("uploading done..")
#
#        return 'HTTP 200 OK'
#
#
#
#    else:
#        slack_client.chat_postMessaged(channel=channel,
#                                  thread_ts=thread_id,
#                                  content="<@"+user+">  Not a supported command.")


def process_message():

    while True:
        msg = q.get()
        blocks = (msg.get('event').get('blocks'))
        user_id = (blocks[-1].get('elements')[-1].get('elements')[0].get('user_id'))
        user = msg.get('event').get('user')

        channel = msg.get('event').get('channel')
        print("******")
        print(channel)
        print("*******")
        thread_id = msg.get('event').get('ts')
        text = (blocks[-1].get('elements')[-1].get('elements')[1].get('text'))

        if text.replace(" ","") == 'help':
            slack_client.chat_postMessage(channel=channel,
                                  thread_ts=thread_id,
                                  text="""<@"""+user+""">  Following commands are supported...
                                  \n #. 1. download logs from <environment name> from device <device name> with search string <search string> from time <from time ust> to <to time ust>
                                  \n #. 2. download logs from <evnironment name> from device <device name> from time <from time ust> to <to time ust>
                                  \n #. 3. downloads logs from <environment name> from microservice with search string <search string> from time <from time ust> to <to time ust>)
                                  \n #. 4. download logs from <environment name> from microservcice <service name> with search string <search string> from time <from time ust> to <to time ust>
                                  \n #. 5. downloads logs from <environment name> from microservice from time <from time ust> to <to time ust>
                                  \n #. 6. download logs from <environment name> from microservcice <service name> from time <from time ust> to <to time ust>
                                  \n #. 7. Note : Use capital 'AND' or 'OR' if you want to include 'AND' or 'OR' in search string
                                  \n #. 8. Format for time : from time : 2022-07-08T07:30:00.000Z to time: 2022-07-08T10:00:00.000Z
                                  \n #  9. ------------------------------------------Sample Usage---------------------------------------------------------------------------------------------------""")

        elif 'download' in text:
            result = slack_client.chat_postMessage(channel=channel,
                                  thread_ts=thread_id,
                                  text="<@"+user+">  Request started. Will update once completed")


            print(result)

            logs = elastic_search.parse_command(text)

            #print(type(logs))

            #print("*****")
            #print(logs)

            with open('/home/pocuser/logs.txt', 'w') as f:
                f.write(logs)


            print("uploaidn gthe logs..")

            result =  slack_client.files_upload(channels=channel,
                                  filename='logs.txt',
                                  title = 'Logs..',
                                  filetype= 'text',
                                  thread_ts=thread_id,
                                  initial_comment = "<@"+user+"> Please find the logs",
                                  file = '/home/pocuser/logs.txt')

            print(result)

            print("uploading done..")

            #return 'HTTP 200 OK'



        else:
            slack_client.chat_postMessaged(channel=channel,
                                  thread_ts=thread_id,
                                  content="<@"+user+">  Not a supported command.")
        q.task_done()




if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
