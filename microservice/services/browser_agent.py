import asyncio
import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add the parent directory to the Python path so we can import browser_use
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from browser_use import Agent
from utils.logger import setup_logger

logger = setup_logger()

class BrowserAgentService:
    def __init__(self):
        # Initialize LLM based on available environment variables
        self.llm = None
        
        try:
            if os.getenv("OPENAI_API_KEY"):
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                logger.info("Initialized OpenAI LLM")
            elif os.getenv("ANTHROPIC_API_KEY"):
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                logger.info("Initialized Anthropic LLM")
            elif os.getenv("DEEPSEEK_API_KEY"):
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner"),
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com"
                )
                logger.info("Initialized DeepSeek LLM")
            else:
                logger.warning("No valid LLM API key found in environment variables")
        except ImportError as e:
            logger.error(f"Failed to import LLM provider: {str(e)}")
            logger.error("Please install the required langchain packages: pip install langchain-openai langchain-anthropic")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
        
        if self.llm is None:
            raise ValueError(
                "No valid LLM could be initialized. Please check:\n"
                "1. Install required packages: pip install langchain-openai langchain-anthropic\n"
                "2. Set a valid API key: OPENAI_API_KEY, ANTHROPIC_API_KEY, or DEEPSEEK_API_KEY"
            )
    
        # Create temporary directory for media files
        self.temp_dir = tempfile.mkdtemp(prefix="browser_agent_")
        logger.info(f"Created temporary directory for media files: {self.temp_dir}")

    async def run_task(self, task_description: str, starting_url: str = None, 
                      timeout: int = 300) -> Tuple[List[Dict], List[str], str]:
        """
        Run a browser automation task and return structured results
        
        Args:
            task_description: The task to perform
            starting_url: Optional starting URL
            timeout: Task timeout in seconds
            
        Returns:
            Tuple of (agent_history, media_file_paths, result_summary)
        """
        try:
            logger.info(f"Creating agent for task: {task_description}")
            
            # Configure agent with media capture
            agent_config = {
                'task': task_description,
                'llm': self.llm,
                'use_vision': True,
                'save_conversation_path': None,  # Disable saving conversations in microservice mode
                'headless': True,  # Run in headless mode for server deployment
            }
            
            # Add starting URL if provided
            if starting_url:
                agent_config['starting_url'] = starting_url
            
            agent = Agent(**agent_config)
            
            # Set up media capture directory
            media_dir = os.path.join(self.temp_dir, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(media_dir, exist_ok=True)
            
            logger.info(f"Running agent with timeout: {timeout}s")
            
            # Run with timeout
            result = await asyncio.wait_for(
                agent.run(), 
                timeout=timeout
            )
            
            # Extract agent history
            agent_history = self._extract_agent_history(agent)
            
            # Capture final screenshot and any media files
            media_files = await self._capture_media_files(agent, media_dir)
            
            result_summary = str(result)
            
            logger.info(f"Task completed successfully. Generated {len(media_files)} media files.")
            
            return agent_history, media_files, result_summary
            
        except asyncio.TimeoutError:
            raise Exception(f"Task timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            raise

    def _extract_agent_history(self, agent: Agent) -> List[Dict]:
        """
        Extract the conversation history from the agent
        
        Args:
            agent: The browser agent instance
            
        Returns:
            List of history items
        """
        try:
            history = []
            
            # Try to access the agent's conversation history
            if hasattr(agent, 'browser') and hasattr(agent.browser, 'get_history'):
                # If browser has a get_history method
                raw_history = agent.browser.get_history()
                history = self._format_history(raw_history)
            elif hasattr(agent, 'history'):
                # If agent has a direct history attribute
                history = self._format_history(agent.history)
            elif hasattr(agent, '_conversation_history'):
                # Alternative history attribute
                history = self._format_history(agent._conversation_history)
            else:
                # Fallback: create minimal history entry
                logger.warning("Could not extract detailed agent history")
                history = [{
                    'timestamp': datetime.now().isoformat(),
                    'type': 'task_completion',
                    'content': 'Task completed - detailed history not available'
                }]
            
            return history
            
        except Exception as e:
            logger.error(f"Error extracting agent history: {str(e)}")
            return [{
                'timestamp': datetime.now().isoformat(),
                'type': 'error',
                'content': f'Failed to extract history: {str(e)}'
            }]

    def _format_history(self, raw_history) -> List[Dict]:
        """
        Format raw history into a standardized structure
        
        Args:
            raw_history: Raw history from the agent
            
        Returns:
            Formatted history list
        """
        formatted_history = []
        
        try:
            if isinstance(raw_history, list):
                for item in raw_history:
                    if isinstance(item, dict):
                        formatted_item = {
                            'timestamp': item.get('timestamp', datetime.now().isoformat()),
                            'type': item.get('type', 'action'),
                            'content': item.get('content', str(item))
                        }
                        # Add any additional fields that might be useful
                        for key in ['action', 'result', 'screenshot', 'url', 'element']:
                            if key in item:
                                formatted_item[key] = item[key]
                        
                        formatted_history.append(formatted_item)
                    else:
                        formatted_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'type': 'action',
                            'content': str(item)
                        })
            else:
                formatted_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'summary',
                    'content': str(raw_history)
                })
        
        except Exception as e:
            logger.error(f"Error formatting history: {str(e)}")
            formatted_history = [{
                'timestamp': datetime.now().isoformat(),
                'type': 'error',
                'content': f'Failed to format history: {str(e)}'
            }]
        
        return formatted_history

    async def _capture_media_files(self, agent: Agent, media_dir: str) -> List[str]:
        """
        Capture screenshots and videos from the browser session
        
        Args:
            agent: The browser agent instance
            media_dir: Directory to save media files
            
        Returns:
            List of file paths to captured media
        """
        media_files = []
        
        try:
            # Capture final screenshot
            if hasattr(agent, 'browser') and agent.browser:
                screenshot_path = os.path.join(media_dir, f"final_screenshot_{datetime.now().strftime('%H%M%S')}.png")
                
                try:
                    # Try to take a screenshot
                    if hasattr(agent.browser, 'take_screenshot'):
                        await agent.browser.take_screenshot(screenshot_path)
                        media_files.append(screenshot_path)
                        logger.info(f"Captured screenshot: {screenshot_path}")
                    elif hasattr(agent.browser, 'page') and hasattr(agent.browser.page, 'screenshot'):
                        await agent.browser.page.screenshot(path=screenshot_path, full_page=True)
                        media_files.append(screenshot_path)
                        logger.info(f"Captured screenshot: {screenshot_path}")
                except Exception as e:
                    logger.warning(f"Failed to capture screenshot: {str(e)}")
            
            # Look for any existing media files in temp directories
            # This might include screenshots taken during the automation process
            temp_dirs = [self.temp_dir]
            
            # Check common temp locations where browser-use might save files
            common_temp_dirs = [
                os.path.join(os.getcwd(), 'screenshots'),
                os.path.join(os.getcwd(), 'videos'),
                '/tmp/browser_use',
                os.path.join(os.path.expanduser('~'), '.browser_use')
            ]
            
            for temp_dir in common_temp_dirs:
                if os.path.exists(temp_dir):
                    temp_dirs.append(temp_dir)
            
            # Collect existing media files
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm', '.avi')):
                                file_path = os.path.join(root, file)
                                if file_path not in media_files:
                                    media_files.append(file_path)
        
        except Exception as e:
            logger.error(f"Error capturing media files: {str(e)}")
        
        logger.info(f"Captured {len(media_files)} media files")
        return media_files

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {str(e)}")

    def __del__(self):
        """Cleanup when service is destroyed"""
        self.cleanup_temp_files()
