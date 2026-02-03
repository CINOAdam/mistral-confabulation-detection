/**
 * Scenario loader and utilities for pre-configured test scenarios
 */

import type { Scenario, ScenarioIndex, ScenarioIndexEntry } from './types';

/**
 * Load the scenario index
 */
export async function loadScenarioIndex(): Promise<ScenarioIndex> {
	const response = await fetch('/scenarios/index.json');
	if (!response.ok) {
		throw new Error(`Failed to load scenario index: ${response.statusText}`);
	}
	return response.json();
}

/**
 * Load a specific scenario by ID
 */
export async function loadScenario(id: string): Promise<Scenario> {
	// First, get the index to find the path
	const index = await loadScenarioIndex();
	const entry = index.scenarios.find((s) => s.id === id);

	if (!entry) {
		throw new Error(`Scenario not found: ${id}`);
	}

	// Load the scenario from its path
	const response = await fetch(entry.path);
	if (!response.ok) {
		throw new Error(`Failed to load scenario ${id}: ${response.statusText}`);
	}

	return response.json();
}

/**
 * Load a scenario by path (for direct access)
 */
export async function loadScenarioByPath(path: string): Promise<Scenario> {
	const response = await fetch(path);
	if (!response.ok) {
		throw new Error(`Failed to load scenario from ${path}: ${response.statusText}`);
	}
	return response.json();
}

/**
 * Get all scenarios from the index
 */
export async function listScenarios(): Promise<ScenarioIndexEntry[]> {
	const index = await loadScenarioIndex();
	return index.scenarios;
}

/**
 * Filter scenarios by discovery type
 */
export async function filterByDiscovery(
	discovery: 'Strategic Deception' | 'Goal Preservation' | 'Bimodal Processing'
): Promise<ScenarioIndexEntry[]> {
	const scenarios = await listScenarios();

	// Map discovery to category
	const categoryMap = {
		'Strategic Deception': 'strategic_deception',
		'Goal Preservation': 'goal_preservation',
		'Bimodal Processing': 'bimodal_processing'
	};

	const category = categoryMap[discovery];
	return scenarios.filter((s) => s.category === category);
}

/**
 * Get featured scenarios (demonstrating key discoveries)
 */
export async function getFeaturedScenarios(): Promise<ScenarioIndexEntry[]> {
	const scenarios = await listScenarios();
	return scenarios.filter((s) => s.featured);
}

/**
 * Filter scenarios by difficulty
 */
export async function filterByDifficulty(
	difficulty: 'basic' | 'intermediate' | 'advanced'
): Promise<ScenarioIndexEntry[]> {
	const scenarios = await listScenarios();
	return scenarios.filter((s) => s.difficulty === difficulty);
}

/**
 * Filter scenarios by expected regime
 */
export async function filterByRegime(
	regime: 'HONEST' | 'DECEPTIVE'
): Promise<ScenarioIndexEntry[]> {
	const scenarios = await listScenarios();
	return scenarios.filter((s) => s.expected_regime === regime);
}

/**
 * Get category information
 */
export async function getCategoryInfo() {
	const index = await loadScenarioIndex();
	return index.categories;
}
