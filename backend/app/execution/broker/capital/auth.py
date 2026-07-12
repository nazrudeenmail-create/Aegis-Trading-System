"""
Capital.com Auth Manager
"""
import asyncio
import logging
from typing import Optional, Dict
from datetime import datetime
from app.execution.broker.models import ConnectionState
from app.execution.broker.capital.client import CapitalClient

logger = logging.getLogger(__name__)

class CapitalAuthManager:
    """
    Manages Capital.com session lifecycle, heartbeats, and reconnections.
    """
    def __init__(self, api_key: str, identifier: str, password: str, client: CapitalClient):
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.client = client
        self.cst: Optional[str] = None
        self.x_security_token: Optional[str] = None
        
        self.state: ConnectionState = ConnectionState.DISCONNECTED
        self.last_heartbeat: Optional[datetime] = None
        self.reconnects_today: int = 0
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        """Authenticate and start heartbeat."""
        self.state = ConnectionState.AUTHENTICATING
        logger.info("Authenticating with Capital.com...")
        
        payload = {
            "identifier": self.identifier,
            "password": self.password,
            "encryptedPassword": False
        }
        
        try:
            # POST /session requires API key but no CST yet
            headers = {
                "X-CAP-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Using client's raw POST since it doesn't have CST yet
            response = await self.client.raw_post("/session", payload, headers)
            
            self.cst = response.headers.get('CST')
            self.x_security_token = response.headers.get('X-SECURITY-TOKEN')
            
            if not self.cst or not self.x_security_token:
                logger.error("Capital.com auth failed: Missing CST or X-SECURITY-TOKEN in response headers.")
                self.state = ConnectionState.ERROR
                return False
                
            self.state = ConnectionState.CONNECTED
            self.last_heartbeat = datetime.now()
            logger.info("Capital.com session established.")
            
            if not self._heartbeat_task or self._heartbeat_task.done():
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
            return True
        except Exception as e:
            logger.error(f"Capital.com authentication exception: {e}")
            self.state = ConnectionState.ERROR
            return False

    async def disconnect(self):
        """Cleanly close session."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        
        if self.state == ConnectionState.CONNECTED and self.cst and self.x_security_token:
            try:
                # To log out, send DELETE /session (using raw request in client)
                headers = self.client._get_headers(self.cst, self.x_security_token)
                await self.client.raw_delete("/session", headers)
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
                
        self.cst = None
        self.x_security_token = None
        self.state = ConnectionState.DISCONNECTED
        logger.info("Capital.com session closed.")

    async def _heartbeat_loop(self):
        """Background task to ping the session and reconnect if it dies."""
        # Capital.com token expires every 10 mins usually, but pinging keeps it alive.
        # We ping every 1 minute.
        while self.state in [ConnectionState.CONNECTED, ConnectionState.RECONNECTING]:
            await asyncio.sleep(60) 
            try:
                if self.state == ConnectionState.CONNECTED:
                    # Ping GET /session
                    await self.client.get("/session", self.cst, self.x_security_token)
                    self.last_heartbeat = datetime.now()
                    logger.debug("Capital.com heartbeat OK")
            except Exception as e:
                logger.warning(f"Capital.com heartbeat failed: {e}")
                self.state = ConnectionState.RECONNECTING
                self.reconnects_today += 1
                success = await self.connect()
                if not success:
                    logger.error("Capital.com reconnection failed.")
                    # Wait longer before retrying
                    await asyncio.sleep(30)
