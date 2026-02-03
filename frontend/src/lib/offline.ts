/**
 * Offline data loader for static HTML export
 *
 * Provides sample activation data when backend is unavailable,
 * enabling the app to work as a standalone static site.
 */

import type {
	ChatResponse,
	ScenarioConfig,
	SAEFeature,
	EarlyLayerActivations,
	LateLayerActivations
} from './api';

// Sample activation data structure
interface SampleActivationData {
	scenario_id: string;
	prompt: string;
	response: string;
	early_activations: EarlyLayerActivations[];
	late_activations: LateLayerActivations;
	sae_features: SAEFeature[];
	regime_classification: 'HONEST' | 'DECEPTIVE';
	l3_l4_distance: number;
	metadata: {
		model: string;
		temperature: number;
		processing_time_ms: number;
	};
}

interface OfflineDataSet {
	version: string;
	captured_at: string;
	scenarios: SampleActivationData[];
}

let offlineData: OfflineDataSet | null = null;

/**
 * Load offline sample data
 */
async function loadOfflineData(): Promise<OfflineDataSet> {
	if (offlineData) {
		return offlineData;
	}

	try {
		const response = await fetch('/data/sample_activations.json');
		if (!response.ok) {
			throw new Error('Failed to load offline data');
		}
		offlineData = await response.json();
		return offlineData;
	} catch (error) {
		console.error('Failed to load offline data:', error);
		throw new Error('Offline data not available');
	}
}

/**
 * Check if backend is available
 */
export async function isBackendAvailable(): Promise<boolean> {
	try {
		const response = await fetch('/health', {
			method: 'GET',
			cache: 'no-cache',
			signal: AbortSignal.timeout(2000) // 2 second timeout
		});
		return response.ok;
	} catch (error) {
		return false;
	}
}

/**
 * Load scenario data from offline cache
 */
export async function loadOfflineScenarioData(scenario_id: string): Promise<SampleActivationData | null> {
	try {
		const data = await loadOfflineData();
		const scenario = data.scenarios.find(s => s.scenario_id === scenario_id);
		return scenario || null;
	} catch (error) {
		console.error(`Failed to load offline data for scenario ${scenario_id}:`, error);
		return null;
	}
}

/**
 * Get all available offline scenarios
 */
export async function getOfflineScenarios(): Promise<string[]> {
	try {
		const data = await loadOfflineData();
		return data.scenarios.map(s => s.scenario_id);
	} catch (error) {
		console.error('Failed to get offline scenarios:', error);
		return [];
	}
}

/**
 * Convert offline data to ChatResponse format
 */
export function convertToMessageFormat(data: SampleActivationData): ChatResponse {
	return {
		message: {
			role: 'assistant',
			content: data.response,
			timestamp: new Date().toISOString()
		},
		activations: {
			early_activations: data.early_activations,
			late_activations: data.late_activations,
			sae_features: data.sae_features,
			regime_classification: data.regime_classification,
			l3_l4_distance: data.l3_l4_distance
		},
		metadata: data.metadata
	};
}

/**
 * Get sample data info for display
 */
export async function getOfflineDataInfo(): Promise<{
	version: string;
	captured_at: string;
	scenario_count: number;
}> {
	try {
		const data = await loadOfflineData();
		return {
			version: data.version,
			captured_at: data.captured_at,
			scenario_count: data.scenarios.length
		};
	} catch (error) {
		return {
			version: 'unknown',
			captured_at: 'unknown',
			scenario_count: 0
		};
	}
}

/**
 * Check if a specific scenario has offline data
 */
export async function hasOfflineData(scenario_id: string): Promise<boolean> {
	try {
		const data = await loadOfflineData();
		return data.scenarios.some(s => s.scenario_id === scenario_id);
	} catch (error) {
		return false;
	}
}
