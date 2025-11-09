"""
Jenkins Integration Module - Provides Jenkins API integration functionality
"""

import os
from typing import Dict, Any, Optional
from jenkinsapi.jenkins import Jenkins
from behavior_framework.utils.logger import Logger


class JenkinsIntegration:
    """Jenkins integration class"""
    
    def __init__(self, jenkins_url: str, username: Optional[str] = None, 
                 password: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize Jenkins connection
        
        Args:
            jenkins_url: Jenkins server URL
            username: Username
            password: Password
            api_token: API Token (if using token authentication)
        """
        self.jenkins_url = jenkins_url
        self.username = username or os.getenv("JENKINS_USERNAME")
        self.password = password or os.getenv("JENKINS_PASSWORD")
        self.api_token = api_token or os.getenv("JENKINS_API_TOKEN")
        self.logger = Logger()
        self.jenkins = None
    
    def connect(self) -> Jenkins:
        """Connect to Jenkins server"""
        try:
            if self.api_token:
                # Use API Token authentication
                self.jenkins = Jenkins(
                    self.jenkins_url,
                    username=self.username,
                    password=self.api_token
                )
            elif self.username and self.password:
                # Use username/password authentication
                self.jenkins = Jenkins(
                    self.jenkins_url,
                    username=self.username,
                    password=self.password
                )
            else:
                # No authentication
                self.jenkins = Jenkins(self.jenkins_url)
            
            self.logger.info(f"Successfully connected to Jenkins: {self.jenkins_url}")
            return self.jenkins
        except Exception as e:
            self.logger.error(f"Failed to connect to Jenkins: {str(e)}")
            raise
    
    def trigger_job(self, job_name: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """
        Trigger Jenkins job
        
        Args:
            job_name: Job name
            parameters: Job parameters
            
        Returns:
            Build number
        """
        if not self.jenkins:
            self.connect()
        
        try:
            job = self.jenkins[job_name]
            if parameters:
                build = job.invoke(build_params=parameters)
            else:
                build = job.invoke()
            
            build_number = build.get_number()
            self.logger.info(f"Triggered Jenkins job: {job_name}, build number: {build_number}")
            return build_number
        except Exception as e:
            self.logger.error(f"Failed to trigger Jenkins job: {str(e)}")
            raise
    
    def get_build_status(self, job_name: str, build_number: int) -> str:
        """
        Get build status
        
        Args:
            job_name: Job name
            build_number: Build number
            
        Returns:
            Build status
        """
        if not self.jenkins:
            self.connect()
        
        try:
            job = self.jenkins[job_name]
            build = job.get_build(build_number)
            status = build.get_status()
            self.logger.info(f"Build status: {job_name} #{build_number} - {status}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to get build status: {str(e)}")
            raise
    
    def get_build_result(self, job_name: str, build_number: int) -> Dict[str, Any]:
        """
        Get build result
        
        Args:
            job_name: Job name
            build_number: Build number
            
        Returns:
            Build result dictionary
        """
        if not self.jenkins:
            self.connect()
        
        try:
            job = self.jenkins[job_name]
            build = job.get_build(build_number)
            
            result = {
                "status": build.get_status(),
                "duration": build.get_duration(),
                "timestamp": build.get_timestamp(),
                "url": build.get_build_url(),
                "console_output": build.get_console()
            }
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to get build result: {str(e)}")
            raise
