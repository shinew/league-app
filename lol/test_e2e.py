import lol.task as task
import lol.riot_queue as queue

queue.add_task(task.MatchList(48675742))

queue.start()
