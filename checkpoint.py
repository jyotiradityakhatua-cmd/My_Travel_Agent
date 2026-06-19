from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = MemorySaver()

checkpointer = SqliteSaver.from_conn_string( "travel_agent.db" )