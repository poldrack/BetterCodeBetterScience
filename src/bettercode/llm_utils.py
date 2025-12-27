from typing import Optional
from anthropic import Anthropic

def send_prompt_to_claude(prompt: str, client: Anthropic, 
                          model: str = "claude-3-5-haiku-latest", 
                          max_tokens: int = 1000, 
                          return_tokens: bool = False) -> Optional[str]:
    """
    Send a prompt to Claude API and return the response.
    
    Args:
        prompt (str): The prompt to send to Claude
        model (str): The Claude model to use
        max_tokens (int): Maximum number of tokens in the response
    
    Returns:
        str: The response from Claude, or None if there was an error
    """
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        if return_tokens:
            return message.content[0].text, message.usage.input_tokens + message.usage.output_tokens
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None