/**
 * TypeScript type definitions for Mistral Reproducibility App
 */

// Chat message structure
export interface ChatMessage {
	role: 'user' | 'assistant' | 'system';
	content: string;
	timestamp: string;
}

// Regime classification based on L3/L4 distance
export type RegimeClassification = 'HONEST' | 'DECEPTIVE';

// SAE feature with activation strength
export interface SAEFeature {
	idx: number;
	activation: number;
	description?: string;
	layer?: number;
}

// Complete activation data for a generation (simplified backend format)
export interface ActivationData {
	early_activations: Record<number, number[]>;  // {1: [floats], 2: [floats], ...}
	late_activations: number[];
	sae_features: SAEFeature[];
	regime_classification: RegimeClassification;
	regime_distance: number;
}

// Complete message with activations
export interface MessageWithActivations {
	message: ChatMessage;
	activations?: ActivationData;
}

// Conversation state
export interface ConversationState {
	id: string;
	messages: MessageWithActivations[];
	created_at: string;
	updated_at: string;
}

// Scenario metadata
export interface ScenarioMetadata {
	difficulty: 'basic' | 'intermediate' | 'advanced';
	category: string;
	created: string;
	expected_behavior?: string;
	theory?: string;
}

// Test scenario
export interface Scenario {
	id: string;
	title: string;
	description: string;
	discovery: 'Strategic Deception' | 'Goal Preservation' | 'Bimodal Processing';
	expected_regime: RegimeClassification;
	expected_distance_range: [number, number];
	prompt: string;
	context: string;
	metadata: ScenarioMetadata;
}

// Scenario index entry
export interface ScenarioIndexEntry {
	id: string;
	path: string;
	title: string;
	category: string;
	expected_regime: RegimeClassification;
	difficulty: 'basic' | 'intermediate' | 'advanced';
	featured: boolean;
}

// Category information
export interface ScenarioCategory {
	name: string;
	description: string;
	discovery: string;
	scenario_count: number;
}

// Complete scenario index
export interface ScenarioIndex {
	version: string;
	last_updated: string;
	total_scenarios: number;
	categories: {
		strategic_deception: ScenarioCategory;
		goal_preservation: ScenarioCategory;
		bimodal_processing: ScenarioCategory;
	};
	scenarios: ScenarioIndexEntry[];
	usage_instructions: {
		loading: string;
		featured: string;
		testing: string;
	};
}
