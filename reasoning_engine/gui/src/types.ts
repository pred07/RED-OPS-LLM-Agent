export interface TargetPort {
  service: string;
  version: string;
  state: string;
}

export interface Target {
  ip: string;
  hostname: string;
  os: string;
  access_level: string;
  ports: Record<string, TargetPort>;
  users: string[];
  creds: string[];
}

export interface ChatMessage {
  type: 'tool' | 'ai' | 'user';
  content: string;
  sender: string;
  timestamp: string;
}
