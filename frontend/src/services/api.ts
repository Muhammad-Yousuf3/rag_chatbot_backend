/**
 * Backend API client service for RAG Chatbot
 *
 * For Docusaurus integration, the API_BASE_URL must be configured at build time
 * or use the runtime configuration below.
 */

/**
 * Get the API base URL from various sources (Docusaurus-compatible).
 *
 * Priority:
 * 1. Window global (set by Docusaurus customFields or external script)
 * 2. Environment variable (for build-time configuration)
 * 3. Hardcoded production URL
 * 4. Localhost for development
 *
 * For production, set window.RAG_CHATBOT_API_URL in your Docusaurus config
 * or via a script tag before loading the app.
 */
function getApiBaseUrl(): string {
  // Check for runtime configuration (Docusaurus customFields or external config)
  if (typeof window !== 'undefined') {
    // Check window global (can be set via Docusaurus customFields or script)
    const windowConfig = (window as Window & { RAG_CHATBOT_API_URL?: string }).RAG_CHATBOT_API_URL;
    if (windowConfig) {
      return windowConfig;
    }

    // Check if running on Vercel production domain
    const hostname = window.location?.hostname || '';
    if (hostname.includes('vercel.app') || hostname.includes('physical-ai-humanoid')) {
      // Production: Use Hugging Face backend URL
      return 'https://muhammadyousuf333-rag-chatbot-with-book.hf.space';
    }
  }

  // Default to localhost for development
  return 'http://localhost:8000';
}

const API_BASE_URL = getApiBaseUrl();

/**
 * API Error class for handling backend errors
 */
export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Source reference from RAG retrieval
 */
export interface SourceReference {
  chapter: string;
  section?: string;
  relevance: number;
}

/**
 * Chat request payload
 */
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

/**
 * Selected text chat request payload
 */
export interface SelectedTextRequest {
  message: string;
  selected_text: string;
  conversation_id?: string;
}

/**
 * Chat response from backend
 */
export interface ChatResponse {
  message: string;
  conversation_id: string;
  sources: SourceReference[];
  is_covered: boolean;
}

/**
 * Health check response
 */
export interface HealthResponse {
  status: 'healthy' | 'degraded';
  timestamp: string;
  services: {
    database: 'up' | 'down';
    qdrant: 'up' | 'down';
    gemini: 'up' | 'down';
  };
}

/**
 * Translation response
 */
export interface TranslationResponse {
  chapter_slug: string;
  language: string;
  content: string;
  created_at: string;
}

/**
 * Translation pending response
 */
export interface TranslationPendingResponse {
  chapter_slug: string;
  language: string;
  status: 'pending' | 'in_progress';
  estimated_seconds?: number;
}

/**
 * User response
 */
export interface UserResponse {
  id: string;
  email: string;
  display_name?: string;
  experience_level?: string;
  preferred_language?: string;
  chapters_read?: string[];
  created_at?: string;
}

/**
 * Auth token response
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

/**
 * Conversation summary
 */
export interface ConversationSummary {
  id: string;
  mode: string;
  message_count: number;
  last_message_preview?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Conversation list response
 */
export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
}

/**
 * Message in conversation
 */
export interface MessageResponse {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

/**
 * Conversation detail response
 */
export interface ConversationDetailResponse {
  id: string;
  user_id?: string;
  mode: string;
  selected_text?: string;
  messages: MessageResponse[];
  created_at: string;
  updated_at: string;
}

/**
 * Generic API fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add auth token if available
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('auth_token')
    : null;
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.error?.code || 'UNKNOWN_ERROR',
      errorData.error?.message || `Request failed with status ${response.status}`,
      errorData.error?.details
    );
  }

  return response.json();
}

/**
 * API fetch with auth token
 */
async function apiFetchWithAuth<T>(
  endpoint: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.error?.code || 'UNKNOWN_ERROR',
      errorData.detail || errorData.error?.message || `Request failed with status ${response.status}`,
      errorData.error?.details
    );
  }

  return response.json();
}

/**
 * API client object with all endpoints
 */
export const api = {
  /**
   * Health check endpoint
   */
  health: async (): Promise<HealthResponse> => {
    return apiFetch<HealthResponse>('/api/health');
  },

  /**
   * Send a chat message (full book mode)
   */
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    return apiFetch<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Send a chat message (selected text mode)
   */
  chatSelected: async (request: SelectedTextRequest): Promise<ChatResponse> => {
    return apiFetch<ChatResponse>('/api/chat/selected', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Register a new user
   */
  register: async (
    email: string,
    password: string,
    displayName?: string
  ): Promise<TokenResponse> => {
    return apiFetch<TokenResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        display_name: displayName,
      }),
    });
  },

  /**
   * Login user
   */
  login: async (email: string, password: string): Promise<TokenResponse> => {
    return apiFetch<TokenResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  /**
   * Get current user
   */
  getCurrentUser: async (token: string): Promise<UserResponse> => {
    return apiFetchWithAuth<UserResponse>('/api/auth/me', token);
  },

  /**
   * Update user preferences
   */
  updatePreferences: async (
    token: string,
    preferences: {
      experience_level?: string;
      preferred_language?: string;
    }
  ): Promise<UserResponse> => {
    return apiFetchWithAuth<UserResponse>('/api/auth/preferences', token, {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  },

  /**
   * Get user's conversations
   */
  getConversations: async (
    token: string,
    limit?: number,
    offset?: number
  ): Promise<ConversationListResponse> => {
    const params = new URLSearchParams();
    if (limit) params.set('limit', String(limit));
    if (offset) params.set('offset', String(offset));
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiFetchWithAuth<ConversationListResponse>(
      `/api/chat/conversations${query}`,
      token
    );
  },

  /**
   * Get conversation detail
   */
  getConversation: async (
    token: string,
    conversationId: string
  ): Promise<ConversationDetailResponse> => {
    return apiFetchWithAuth<ConversationDetailResponse>(
      `/api/chat/conversations/${conversationId}`,
      token
    );
  },

  /**
   * Get chapter translation
   */
  getTranslation: async (
    chapterSlug: string,
    language: string = 'ur'
  ): Promise<TranslationResponse | TranslationPendingResponse> => {
    return apiFetch(`/api/translate/${chapterSlug}?language=${language}`);
  },

  /**
   * Request chapter translation
   */
  requestTranslation: async (
    chapterSlug: string,
    content?: string,
    language: string = 'ur'
  ): Promise<TranslationResponse | TranslationPendingResponse> => {
    return apiFetch(`/api/translate/${chapterSlug}`, {
      method: 'POST',
      body: JSON.stringify({ language, content }),
    });
  },
};

/**
 * Chat API helper object for cleaner imports
 */
export const chatApi = {
  sendMessage: api.chat,
  sendSelectedTextMessage: api.chatSelected,
  getTranslation: api.getTranslation,
  requestTranslation: api.requestTranslation,
};

/**
 * Auth API helper object
 */
export const authApi = {
  register: api.register,
  login: api.login,
  getCurrentUser: api.getCurrentUser,
  updatePreferences: api.updatePreferences,
  getConversations: api.getConversations,
  getConversation: api.getConversation,
};

export default api;
