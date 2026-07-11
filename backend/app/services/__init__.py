# Services module — Application layer
# Handles: business workflow orchestration between API routes and trading modules
# Services sit between the API layer and the Trading Engine.
#
# Architecture:
#   API Route → Service → Repository / Trading Module
#
# Future services (Phase 10+):
#   - MarketDataService
#   - StrategyService
#   - RiskService
#   - TradeService
#   - NotificationService
