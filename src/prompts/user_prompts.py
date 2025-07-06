"""
User prompt templates and formatting
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

class UserPrompts:
    """Collection of user prompt templates and formatters"""
    
    @classmethod
    def format_user_message(cls, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format user message with optional context
        
        Args:
            content: User message content
            context: Optional context information
            
        Returns:
            Formatted user message
        """
        if not context:
            return content
        
        formatted_message = content
        
        # Add timestamp if not present
        if "timestamp" not in context:
            formatted_message += f"\n[Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
        
        # Add location context if available
        if "location" in context:
            formatted_message += f"\n[User location: {context['location']}]"
        
        # Add current task context if available
        if "current_task" in context:
            formatted_message += f"\n[Current task: {context['current_task']}]"
        
        return formatted_message
    
    @classmethod
    def create_task_prompt(cls, task_description: str, requirements: List[str] = None,
                          constraints: List[str] = None) -> str:
        """
        Create a structured task prompt
        
        Args:
            task_description: Main task description
            requirements: List of requirements
            constraints: List of constraints
            
        Returns:
            Formatted task prompt
        """
        prompt = f"TASK: {task_description}\n\n"
        
        if requirements:
            prompt += "REQUIREMENTS:\n"
            for i, req in enumerate(requirements, 1):
                prompt += f"{i}. {req}\n"
            prompt += "\n"
        
        if constraints:
            prompt += "CONSTRAINTS:\n"
            for i, constraint in enumerate(constraints, 1):
                prompt += f"{i}. {constraint}\n"
            prompt += "\n"
        
        prompt += "Please complete this task step by step and explain your approach."
        
        return prompt
    
    @classmethod
    def create_research_prompt(cls, topic: str, specific_questions: List[str] = None,
                             sources_to_include: List[str] = None) -> str:
        """
        Create a research-focused prompt
        
        Args:
            topic: Research topic
            specific_questions: Specific questions to answer
            sources_to_include: Preferred sources to include
            
        Returns:
            Formatted research prompt
        """
        prompt = f"RESEARCH REQUEST: {topic}\n\n"
        
        if specific_questions:
            prompt += "SPECIFIC QUESTIONS TO ADDRESS:\n"
            for i, question in enumerate(specific_questions, 1):
                prompt += f"{i}. {question}\n"
            prompt += "\n"
        
        if sources_to_include:
            prompt += "PREFERRED SOURCES:\n"
            for source in sources_to_include:
                prompt += f"- {source}\n"
            prompt += "\n"
        
        prompt += "Please provide comprehensive research with reliable sources and clear citations."
        
        return prompt
    
    @classmethod
    def create_analysis_prompt(cls, data_description: str, analysis_type: str,
                             output_format: str = "summary") -> str:
        """
        Create an analysis prompt
        
        Args:
            data_description: Description of data to analyze
            analysis_type: Type of analysis needed
            output_format: Desired output format
            
        Returns:
            Formatted analysis prompt
        """
        prompt = "DATA ANALYSIS REQUEST\n\n"
        prompt += f"DATA: {data_description}\n\n"
        prompt += f"ANALYSIS TYPE: {analysis_type}\n\n"
        prompt += f"OUTPUT FORMAT: {output_format}\n\n"
        prompt += "Please analyze the data and provide insights with clear explanations."
        
        return prompt
    
    @classmethod
    def create_creative_prompt(cls, creative_task: str, style: Optional[str] = None,
                             length: Optional[str] = None, audience: Optional[str] = None) -> str:
        """
        Create a creative writing prompt
        
        Args:
            creative_task: Creative task description
            style: Writing style preference
            length: Desired length
            audience: Target audience
            
        Returns:
            Formatted creative prompt
        """
        prompt = f"CREATIVE TASK: {creative_task}\n\n"
        
        if style:
            prompt += f"STYLE: {style}\n"
        
        if length:
            prompt += f"LENGTH: {length}\n"
        
        if audience:
            prompt += f"AUDIENCE: {audience}\n"
        
        prompt += "\nPlease create engaging and original content that meets these specifications."
        
        return prompt
    
    @classmethod
    def create_problem_solving_prompt(cls, problem: str, constraints: List[str] = None,
                                    desired_outcome: Optional[str] = None) -> str:
        """
        Create a problem-solving prompt
        
        Args:
            problem: Problem description
            constraints: List of constraints
            desired_outcome: Desired outcome
            
        Returns:
            Formatted problem-solving prompt
        """
        prompt = f"PROBLEM TO SOLVE: {problem}\n\n"
        
        if constraints:
            prompt += "CONSTRAINTS:\n"
            for i, constraint in enumerate(constraints, 1):
                prompt += f"{i}. {constraint}\n"
            prompt += "\n"
        
        if desired_outcome:
            prompt += f"DESIRED OUTCOME: {desired_outcome}\n\n"
        
        prompt += "Please provide a step-by-step solution with reasoning for each step."
        
        return prompt
    
    @classmethod
    def create_learning_prompt(cls, topic: str, current_level: str,
                             learning_goals: List[str] = None) -> str:
        """
        Create a learning-focused prompt
        
        Args:
            topic: Topic to learn about
            current_level: Current knowledge level
            learning_goals: Specific learning goals
            
        Returns:
            Formatted learning prompt
        """
        prompt = f"LEARNING REQUEST: {topic}\n\n"
        prompt += f"CURRENT LEVEL: {current_level}\n\n"
        
        if learning_goals:
            prompt += "LEARNING GOALS:\n"
            for i, goal in enumerate(learning_goals, 1):
                prompt += f"{i}. {goal}\n"
            prompt += "\n"
        
        prompt += "Please provide a structured learning plan with explanations and examples."
        
        return prompt
