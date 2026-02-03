/**
 * API Client for Mistral Reproducibility Backend
 *
 * Handles communication with FastAPI backend for:
 * - Chat interactions with activation capture
 * - Pre-configured scenario loading
 * - Activation data retrieval and analysis
 */

// Backend API URL - configurable via environment variable
const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000';

export interface ChatMessage {
	role: 'user' | 'assistant' | 'system';
	content: string;
	timestamp?: string;
}

export interface SAEFeature {
	idx: number;
	activation: number;
	description?: string;
	layer?: number;
}

export interface ScenarioConfig {
	id: string;
	name: string;
	description: string;
	initial_prompt: string;
	follow_up_prompts: string[];
	expected_discovery: string;
}

// Backend response format (simplified)
export interface ChatResponse {
	response: string;
	early_activations: Record<number, number[]>;  // {1: [floats], 2: [floats], ...}
	late_activations: number[];
	sae_features: SAEFeature[];
	regime_distance: number;
	regime_classification: 'HONEST' | 'DECEPTIVE';
	timestamp: string;
}

/**
 * Send a chat message and receive response with activations
 */
export async function sendChatMessage(
	message: string,
	conversation_history: ChatMessage[] = []
): Promise<{ message: ChatMessage; activations: any }> {
	// Build messages array from conversation history + new message
	const messages = [
		...conversation_history,
		{ role: 'user' as const, content: message }
	];

	const response = await fetch(`${BACKEND_API_URL}/v1/chat`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			messages,
			max_new_tokens: 150
		})
	});

	if (!response.ok) {
		throw new Error(`API request failed: ${response.statusText}`);
	}

	const data: ChatResponse = await response.json();

	// Transform backend response to frontend format
	return {
		message: {
			role: 'assistant',
			content: data.response,
			timestamp: data.timestamp
		},
		activations: {
			early_activations: data.early_activations,
			late_activations: data.late_activations,
			sae_features: data.sae_features,
			regime_classification: data.regime_classification,
			regime_distance: data.regime_distance
		}
	};
}

/**
 * Load a pre-configured scenario
 */
export async function loadScenario(scenario_id: string): Promise<ScenarioConfig> {
	const response = await fetch(`${BACKEND_API_URL}/api/scenarios/${scenario_id}`);

	if (!response.ok) {
		throw new Error(`Failed to load scenario: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Get list of available scenarios
 */
export async function getScenarios(): Promise<ScenarioConfig[]> {
	const response = await fetch(`${BACKEND_API_URL}/api/scenarios`);

	if (!response.ok) {
		throw new Error(`Failed to fetch scenarios: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Analyze activations for a specific conversation turn
 */
export async function analyzeActivations(
	conversation_id: string,
	turn_index: number
): Promise<{
	strategic_deception_score: number;
	goal_preservation_score: number;
	bimodal_processing_detected: boolean;
	key_layers: number[];
	explanation: string;
}> {
	const response = await fetch(
		`${BACKEND_API_URL}/api/analyze/${conversation_id}/${turn_index}`
	);

	if (!response.ok) {
		throw new Error(`Failed to analyze activations: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Health check for backend connectivity
 */
export async function healthCheck(): Promise<boolean> {
	try {
		const response = await fetch(`${BACKEND_API_URL}/health`, {
			method: 'GET',
			cache: 'no-cache'
		});
		return response.ok;
	} catch (error) {
		console.error('Backend health check failed:', error);
		return false;
	}
}

/**
 * Export conversation and activations as JSON
 */
export async function exportConversation(conversation_id: string): Promise<Blob> {
	const response = await fetch(`${BACKEND_API_URL}/api/export/${conversation_id}`);

	if (!response.ok) {
		throw new Error(`Failed to export conversation: ${response.statusText}`);
	}

	return await response.blob();
}

/**
 * Get annotation for a single SAE feature
 */
export async function getFeatureAnnotation(
	featureIdx: number,
	layer: number = 30
): Promise<{
	idx: number;
	description: string;
	layer: number;
	neuronpedia_url: string;
}> {
	const response = await fetch(`${BACKEND_API_URL}/api/features/${featureIdx}?layer=${layer}`);

	if (!response.ok) {
		throw new Error(`Failed to fetch feature annotation: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Get annotations for multiple SAE features
 */
export async function batchGetFeatureAnnotations(
	featureIndices: number[],
	layer: number = 30,
	forceRefresh: boolean = false
): Promise<{
	features: Array<{
		idx: number;
		description: string;
		layer: number;
		neuronpedia_url: string;
		source: string;
		error?: string;
	}>;
	total: number;
	cached: number;
	fetched: number;
}> {
	const response = await fetch(`${BACKEND_API_URL}/api/features/batch`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			feature_indices: featureIndices,
			layer: layer,
			force_refresh: forceRefresh
		})
	});

	if (!response.ok) {
		throw new Error(`Failed to fetch feature annotations: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Get annotation cache statistics
 */
export async function getAnnotationStats(): Promise<{
	total_cached: number;
	cache_file: string;
	cache_exists: boolean;
}> {
	const response = await fetch(`${BACKEND_API_URL}/api/annotations/stats`);

	if (!response.ok) {
		throw new Error(`Failed to fetch annotation stats: ${response.statusText}`);
	}

	return await response.json();
}
