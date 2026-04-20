export interface User{
    id: string
    email : string
    name : string | null
    provider: "email" | "google"
    createdAt : string
}

export interface ResearchSession{
    id: string
    userId : string
    topic : string
    status : "pending" | "running" | "completed" | "failed"
    reportJson : Record<string , unknown> | null
    errorMessage: string | null
    createdAt : string
    updatedAt : string
}

export interface ChatMessage {
    id: string
    sessionId : string
    role : "user" | "assistant" | "system"
    content : string
    createdAt:string
}

export interface AgentEvent {
    id : string
    sessionId : string
    agentName : string
    eventType : string
    payload : Record<string , unknown> | null
    createdAt: string
}

export interface ApiResponse<T>{
    data: T | null
    error : string | null
}