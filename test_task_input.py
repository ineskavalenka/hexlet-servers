import client

task = client.get_task()
print(task.storypoints, task.description)