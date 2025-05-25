import asyncio
import os
from browser_use import Agent
from langchain_openai import ChatOpenAI
from utils.logger import setup_logger

logger = setup_logger()

class BrowserAgentService:
    def __init__(self):
        # Initialize LLM based on available environment variables
        if os.getenv("OPENAI_API_KEY"):
            self.llm = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif os.getenv("ANTHROPIC_API_KEY"):
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        elif os.getenv("DEEPSEEK_API_KEY"):
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
        else:
            raise ValueError("No valid API key found. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or DEEPSEEK_API_KEY in your environment.")
    
    async def run_task(self, task_description: str, timeout: int = 300) -> str:
        """Run a browser automation task"""
        try:
            logger.info(f"Creating agent for task: {task_description}")
            
            agent = Agent(
                task=task_description,
                llm=self.llm,
                # Add any other configuration options
                use_vision=True,
                save_conversation_path=None,  # Disable saving conversations in microservice mode
            )
            
            # Run with timeout
            result = await asyncio.wait_for(
                agent.run(), 
                timeout=timeout
            )
            
            return str(result)
            
        except asyncio.TimeoutError:
            raise Exception(f"Task timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            raise
