"""AegisFlow — Enterprise AI Agent Runtime Governance Platform.

AegisFlow is the immune system for AI agents in production.
It fills the gap between observability and enforcement,
providing runtime policy execution, budget control, sandbox isolation,
audit trails, and human-in-the-loop gating.

Core modules:
- policy: Declarative policy engine with runtime enforcement
- budget: Token-level cost guard with predictive throttling
- sandbox: Filesystem/process isolation for agent actions
- compress: Content-aware compression à la Headroom
- audit: Immutable agent behavior audit trail
- human_loop: Human approval gateway for high-risk actions
- api: FastAPI REST + WebSocket server
"""

__version__="0.1.0"
__author__="lanekingkong"
