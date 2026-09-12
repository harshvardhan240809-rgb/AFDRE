import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import type { SimulationState } from '../types'

const DEFAULT_SCENARIOS = [
  'Payment Gateway Failure',
  'Database Latency',
  'Inventory Service Failure',
  'API Gateway Failure',
  'Notification Service Failure',
  'Authentication Service Failure',
  'Backup System Unavailable',
  'Network Dependency Failure',
]

function statusColor(status: string) {
  switch (status) {
    case 'HEALTHY':
      return '#35d39a'
    case 'DEGRADED':
      return '#f0b656'
    case 'FAILED':
      return '#ff6b6b'
    case 'RECOVERING':
      return '#73b8ff'
    case 'RECOVERED':
      return '#82e7c1'
    default:
      return '#d5d7de'
  }
}

export default function MAYDAYCommandCenter() {
  const [state, setState] = useState<SimulationState | null>(null)
  const [scenario, setScenario] = useState(DEFAULT_SCENARIOS[0])
  const [isLoading, setIsLoading] = useState(false)
  const [incidents, setIncidents] = useState<any[]>([])
  const [risks, setRisks] = useState<any[]>([])

  useEffect(() => {
    void loadSimulation()
  }, [])

  useEffect(() => {
    if (!state?.simulation_id) return

    const refreshAuditData = async () => {
      try {
        const [incidentData, riskData] = await Promise.all([
          api.getIncidents(),
          api.getRisks(),
        ])
        setIncidents(incidentData)
        setRisks(riskData)
      } catch (error) {
        console.error(error)
      }
    }

    void refreshAuditData()
  }, [state?.simulation_id])

  const loadSimulation = async () => {
    try {
      setIsLoading(true)
      const created = await api.createSimulation()
      setState(created)
      setScenario(created.scenario)
    } catch (error) {
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const runScenario = async () => {
    if (!state) return
    setIsLoading(true)
    try {
      await api.discover(state.simulation_id)
      await api.injectFailure(state.simulation_id, scenario)
      await api.recover(state.simulation_id)
      await api.chaos(state.simulation_id)
      const verified = await api.verify(state.simulation_id)
      setState(verified)
    } catch (error) {
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const runFullDemo = async () => {
    setIsLoading(true)
    try {
      const demoState = await api.fullDemo()
      setState(demoState)
    } catch (error) {
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const healthSummary = useMemo(() => {
    if (!state) return { healthy: 0, degraded: 0, failed: 0 }
    return state.services.reduce(
      (acc, service) => {
        if (service.status === 'HEALTHY') acc.healthy += 1
        if (service.status === 'DEGRADED') acc.degraded += 1
        if (service.status === 'FAILED') acc.failed += 1
        return acc
      },
      { healthy: 0, degraded: 0, failed: 0 },
    )
  }, [state])

  return (
    <div className="command-shell">
      <header className="topbar">
        <div>
          <div className="brand-row">
            <span className="brand-mark">MAYDAY AI</span>
            <span className="badge safe-badge">SAFE SIMULATION MODE</span>
          </div>
          <div className="subheader-row">
            <span>Scenario: {state?.scenario ?? 'Loading...'}</span>
            <span>Simulation Time: {state ? state.current_phase : '---'}</span>
            <span>AI Status: ONLINE</span>
          </div>
        </div>
        <div className="status-cluster">
          <div className="mini-stat">
            <span className="label">System Status</span>
            <strong>{state ? state.current_phase : 'LOADING'}</strong>
          </div>
          <div className="mini-stat">
            <span className="label">Resilience</span>
            <strong>{state ? `${state.resilience_score}/100` : '--'}</strong>
          </div>
        </div>
      </header>

      <main className="dashboard-grid">
        <aside className="panel controls-panel">
          <h3>Controls</h3>
          <div className="stack">
            <button onClick={() => void loadSimulation()} className="primary-button" disabled={isLoading}>Create Simulation</button>
            <button onClick={() => void runScenario()} className="secondary-button" disabled={isLoading || !state}>Run Scenario</button>
            <button onClick={() => void runFullDemo()} className="tertiary-button" disabled={isLoading}>Run Full MAYDAY Scenario</button>
            <label className="select-wrap">
              <span>Failure Scenario</span>
              <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
                {DEFAULT_SCENARIOS.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="summary-box">
            <h4>Service health</h4>
            <div className="health-legend">
              <span>Healthy: {healthSummary.healthy}</span>
              <span>Degraded: {healthSummary.degraded}</span>
              <span>Failed: {healthSummary.failed}</span>
            </div>
          </div>
        </aside>

        <section className="panel graph-panel">
          <h3>Digital Twin</h3>
          {state ? (
            <div className="graph-grid">
              {state.services.map((service) => (
                <div key={service.name} className="service-node" style={{ borderColor: statusColor(service.status) }}>
                  <div className="node-header">
                    <span>{service.name}</span>
                    <span className="status-pill" style={{ background: `${statusColor(service.status)}22`, color: statusColor(service.status) }}>
                      {service.status}
                    </span>
                  </div>
                  <div className="node-body">
                    <small>Health: {service.health}%</small>
                    <small>Latency: {service.latency}ms</small>
                    <small>Load: {service.current_load}%</small>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">Loading Digital Twin...</div>
          )}
        </section>

        <aside className="panel feed-panel">
          <h3>AI Activity Feed</h3>
          <div className="feed-list">
            {state?.agent_events.slice(-10).map((event, index) => (
              <div key={`${event.timestamp}-${event.agent}-${index}`} className="feed-item">
                <div className="feed-time">{event.timestamp.slice(11, 19)}</div>
                <div className="feed-body">
                  <b>{event.agent}</b>
                  <p>{event.message}</p>
                </div>
              </div>
            ))}
          </div>
        </aside>

        <section className="panel bottom-panel">
          <div className="metric-panel">
            <h3>Recovery Plan</h3>
            <ol>
              {state?.recovery_plan.steps.map((step, index) => (
                <li key={`${step}-${index}`}>{step}</li>
              ))}
            </ol>
          </div>
          <div className="metric-panel">
            <h3>Timeline</h3>
            <ul className="timeline">
              {state?.timeline.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="metric-panel">
            <h3>Detected Risks</h3>
            <ul className="metrics-list">
              {risks.length > 0 ? (
                risks.map((risk) => (
                  <li key={risk.id || risk.service}>
                    <strong>{risk.service}</strong> — {risk.severity} ({risk.risk_score}/10)
                  </li>
                ))
              ) : (
                <li>No risks identified yet.</li>
              )}
            </ul>
          </div>
          <div className="metric-panel">
            <h3>Incident History</h3>
            <ul className="metrics-list">
              {incidents.length > 0 ? (
                incidents.slice(0, 5).map((incident) => (
                  <li key={incident.incident_id || incident.timestamp}>
                    <strong>{incident.failure_type}</strong> — {incident.verification_result}
                  </li>
                ))
              ) : (
                <li>No incidents recorded yet.</li>
              )}
            </ul>
          </div>
          <div className="metric-panel">
            <h3>Metrics</h3>
            <ul className="metrics-list">
              <li>Recovery Time: {state?.metrics.recovery_time ?? 0}</li>
              <li>System Stability: {state?.metrics.system_stability ?? 0}</li>
              <li>Data Integrity: {state?.metrics.data_integrity ?? 0}</li>
              <li>Adaptability: {state?.metrics.adaptability ?? 0}</li>
              <li>Business Impact: {state?.metrics.business_impact ?? 0}</li>
            </ul>
          </div>
        </section>
      </main>
    </div>
  )
}
