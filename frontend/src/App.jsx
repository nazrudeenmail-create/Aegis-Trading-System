import { useEffect, useState } from "react";
import { checkHealth } from "./api/health";

function App() {
  const [backendStatus, setBackendStatus] = useState("checking...");
  const [serviceName, setServiceName] = useState("");
  const [version, setVersion] = useState("");
  const [environment, setEnvironment] = useState("");

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setBackendStatus(data.status);
        setServiceName(data.service);
        setVersion(data.version);
        setEnvironment(data.environment);
      })
      .catch(() => {
        setBackendStatus("unreachable");
      });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl p-10 max-w-lg w-full text-center">
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Aegis Trading System
        </h1>
        <p className="text-gray-400 text-sm mb-8">
          Professional Rule-Based Algorithmic Trading Platform
        </p>

        <div className="space-y-3 text-left bg-gray-800 rounded-lg p-5 border border-gray-700">
          <Row label="Backend" value={backendStatus} />
          <Row label="Service" value={serviceName || "—"} />
          <Row label="Version" value={version || "—"} />
          <Row label="Environment" value={environment || "—"} />
        </div>

        <p className="text-xs text-gray-500 mt-6">
          Accuracy > Speed > Profit
        </p>
      </div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-400">{label}</span>
      <span className="text-gray-100 font-mono">{value}</span>
    </div>
  );
}

export default App;