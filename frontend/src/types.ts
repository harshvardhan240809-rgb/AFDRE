export type ServiceStatus = 'HEALTHY' | 'DEGRADED' | 'FAILED' | 'RECOVERING' | 'RECOVERED'

export interface Service {
  name: string
  status: ServiceStatus
  health: number
  dependencies: string[]
  current_load: number
  failure_state: boolean
  recovery_state: string
  criticality: string
  latency: number
  availability: number
}

export interface AgentEvent {
  timestamp: string
  agent: string
  message: string
}

export interface RetrievalResult {
  id: string
  title: string
  content: string
  tags: string[]
  confidence: number
}

export interface SimulationState {
  simulation_id: string
  current_phase: string
  scenario: string
  services: Service[]
  dependencies: Record<string, string[]>
  failures: string[]
  active_incidents: string[]
  agent_events: AgentEvent[]
  recovery_plan: { plan_version: string; steps: string[] }
  plan_version: string
  chaos_events: string[]
  metrics: {
    recovery_time: number
    system_stability: number
    data_integrity: number
    adaptability: number
    business_impact: number
  }
  resilience_score: number
  memory_entries: any[]
  risks: any[]
  verification: { status: string; details: Record<string, any> }
  timeline: string[]
  retrieval: { documents: RetrievalResult[]; related_incidents: any[] }
}
