import client from "./client";

/**
 * Check backend health.
 *
 * Calls GET /api/v1/health on the FastAPI backend.
 * Used by the frontend on startup to verify the backend is reachable.
 *
 * @returns {Promise<object>} { status, service, version, environment }
 */
export async function checkHealth() {
  const response = await client.get("/api/v1/health");
  return response.data;
}