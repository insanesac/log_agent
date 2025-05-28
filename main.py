from crewai import Crew, Process
import os

#microcontroller_agent
from agents import PrepAgents
from tasks import PrepTasks

agents = PrepAgents()
tasks = PrepTasks()

crew = Crew(
  agents=[agents.machine_agent(), agents.process_agent()],
  tasks=[tasks.machine_task(), tasks.process_task()],
  memory=True,
  cache=True,
  max_rpm=5,
  share_crew=True
)

inputs = {}
result = crew.kickoff(inputs=inputs)