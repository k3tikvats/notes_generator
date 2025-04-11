import os
from typing import Optional


def get_env_variable(name: str, default: Optional[str] = None, prompt: bool = True) -> str:
    """Get environment variable with optional prompting if not found.
    
    Args:
        name: Environment variable name
        default: Default value if not found
        prompt: Whether to prompt user for input if not found
        
    Returns:
        Environment variable value
    """
    value = os.getenv(name)
    
    if value is None:
        if prompt:
            value = input(f"Please enter {name}: ")
        elif default is not None:
            value = default
        else:
            raise ValueError(f"Environment variable {name} not set and no default provided")
            
    return value


def create_required_directories(directories: list) -> None:
    """Create all required directories if they don't exist.
    
    Args:
        directories: List of directory paths
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}")