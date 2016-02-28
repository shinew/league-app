import lol.task as task
import lol.riot_queue as queue

queue.add_task(task.add_match_list(48675742))

queue.start()
