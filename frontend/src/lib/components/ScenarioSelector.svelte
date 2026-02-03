<script lang="ts">
	import { onMount } from 'svelte';
	import type { ScenarioIndexEntry, Scenario } from '$lib/types';
	import {
		loadScenarioIndex,
		loadScenario,
		getFeaturedScenarios,
		filterByDiscovery
	} from '$lib/scenarios';

	// Props
	export let onScenarioLoad: (scenario: Scenario) => void;

	// State
	let scenarios: ScenarioIndexEntry[] = [];
	let featuredScenarios: ScenarioIndexEntry[] = [];
	let selectedScenarioId: string | null = null;
	let selectedScenario: Scenario | null = null;
	let loading = false;
	let error: string | null = null;
	let viewMode: 'featured' | 'all' | 'discovery' = 'featured';
	let selectedDiscovery: 'Strategic Deception' | 'Goal Preservation' | 'Bimodal Processing' =
		'Strategic Deception';

	// Load scenarios on mount
	onMount(async () => {
		try {
			loading = true;
			const index = await loadScenarioIndex();
			scenarios = index.scenarios;
			featuredScenarios = await getFeaturedScenarios();

			// Auto-select first featured scenario
			if (featuredScenarios.length > 0) {
				selectedScenarioId = featuredScenarios[0].id;
				await handleScenarioSelect();
			}
		} catch (e) {
			error = `Failed to load scenarios: ${e}`;
			console.error(error, e);
		} finally {
			loading = false;
		}
	});

	// Handle scenario selection
	async function handleScenarioSelect() {
		if (!selectedScenarioId) return;

		try {
			loading = true;
			error = null;
			selectedScenario = await loadScenario(selectedScenarioId);
		} catch (e) {
			error = `Failed to load scenario: ${e}`;
			console.error(error, e);
			selectedScenario = null;
		} finally {
			loading = false;
		}
	}

	// Handle load button click
	function handleLoadScenario() {
		if (selectedScenario) {
			onScenarioLoad(selectedScenario);
		}
	}

	// Filter scenarios based on view mode
	$: displayedScenarios =
		viewMode === 'featured'
			? featuredScenarios
			: viewMode === 'all'
				? scenarios
				: scenarios.filter((s) => {
						const categoryMap = {
							'Strategic Deception': 'strategic_deception',
							'Goal Preservation': 'goal_preservation',
							'Bimodal Processing': 'bimodal_processing'
						};
						return s.category === categoryMap[selectedDiscovery];
					});

	// Get regime badge color
	function getRegimeBadgeColor(regime: 'HONEST' | 'DECEPTIVE'): string {
		return regime === 'HONEST' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
	}

	// Get difficulty badge color
	function getDifficultyBadgeColor(
		difficulty: 'basic' | 'intermediate' | 'advanced'
	): string {
		switch (difficulty) {
			case 'basic':
				return 'bg-blue-100 text-blue-800';
			case 'intermediate':
				return 'bg-yellow-100 text-yellow-800';
			case 'advanced':
				return 'bg-purple-100 text-purple-800';
		}
	}
</script>

<div class="scenario-selector bg-white rounded-lg shadow-md p-6 mb-6">
	<div class="header mb-4">
		<h2 class="text-2xl font-bold text-gray-900 mb-2">Pre-configured Scenarios</h2>
		<p class="text-sm text-gray-600">
			Test scenarios demonstrating the three key discoveries: Strategic Deception, Goal
			Preservation, and Bimodal Processing
		</p>
	</div>

	<!-- View mode selector -->
	<div class="view-mode-selector mb-4 flex gap-2">
		<button
			class="px-4 py-2 rounded-md text-sm font-medium transition-colors {viewMode === 'featured'
				? 'bg-indigo-600 text-white'
				: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
			on:click={() => (viewMode = 'featured')}
		>
			Featured (3)
		</button>
		<button
			class="px-4 py-2 rounded-md text-sm font-medium transition-colors {viewMode === 'discovery'
				? 'bg-indigo-600 text-white'
				: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
			on:click={() => (viewMode = 'discovery')}
		>
			By Discovery
		</button>
		<button
			class="px-4 py-2 rounded-md text-sm font-medium transition-colors {viewMode === 'all'
				? 'bg-indigo-600 text-white'
				: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
			on:click={() => (viewMode = 'all')}
		>
			All ({scenarios.length})
		</button>
	</div>

	<!-- Discovery filter (only shown in discovery mode) -->
	{#if viewMode === 'discovery'}
		<div class="discovery-filter mb-4">
			<label for="discovery-select" class="block text-sm font-medium text-gray-700 mb-2">
				Filter by Discovery:
			</label>
			<select
				id="discovery-select"
				bind:value={selectedDiscovery}
				class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
			>
				<option value="Strategic Deception">Strategic Deception</option>
				<option value="Goal Preservation">Goal Preservation</option>
				<option value="Bimodal Processing">Bimodal Processing</option>
			</select>
		</div>
	{/if}

	<!-- Scenario selector -->
	<div class="scenario-list mb-4">
		<label for="scenario-select" class="block text-sm font-medium text-gray-700 mb-2">
			Select Scenario:
		</label>
		<select
			id="scenario-select"
			bind:value={selectedScenarioId}
			on:change={handleScenarioSelect}
			disabled={loading}
			class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100"
		>
			{#each displayedScenarios as scenario}
				<option value={scenario.id}>
					{scenario.title}
					{scenario.featured ? '⭐' : ''}
				</option>
			{/each}
		</select>
	</div>

	<!-- Scenario details -->
	{#if loading}
		<div class="loading-state p-4 bg-gray-50 rounded-md">
			<p class="text-sm text-gray-600">Loading scenario...</p>
		</div>
	{:else if error}
		<div class="error-state p-4 bg-red-50 rounded-md">
			<p class="text-sm text-red-600">{error}</p>
		</div>
	{:else if selectedScenario}
		<div class="scenario-details p-4 bg-gray-50 rounded-md space-y-3">
			<!-- Title and badges -->
			<div class="flex items-start justify-between">
				<h3 class="text-lg font-semibold text-gray-900">{selectedScenario.title}</h3>
				<div class="flex gap-2">
					<span
						class="px-2 py-1 text-xs font-medium rounded-full {getRegimeBadgeColor(
							selectedScenario.expected_regime
						)}"
					>
						{selectedScenario.expected_regime}
					</span>
					<span
						class="px-2 py-1 text-xs font-medium rounded-full {getDifficultyBadgeColor(
							selectedScenario.metadata.difficulty
						)}"
					>
						{selectedScenario.metadata.difficulty}
					</span>
				</div>
			</div>

			<!-- Description -->
			<div>
				<p class="text-sm text-gray-700">{selectedScenario.description}</p>
			</div>

			<!-- Discovery type -->
			<div>
				<span class="text-xs font-medium text-gray-500">Discovery Type:</span>
				<span class="text-sm text-indigo-600 ml-2">{selectedScenario.discovery}</span>
			</div>

			<!-- Prompt -->
			<div>
				<label class="text-xs font-medium text-gray-500 block mb-1">Prompt:</label>
				<div class="bg-white p-3 rounded border border-gray-200">
					<p class="text-sm text-gray-900 font-mono">{selectedScenario.prompt}</p>
				</div>
			</div>

			<!-- Expected outcome -->
			<div>
				<label class="text-xs font-medium text-gray-500 block mb-1">Expected Outcome:</label>
				<div class="bg-white p-3 rounded border border-gray-200 space-y-2">
					<div class="flex items-center justify-between">
						<span class="text-xs text-gray-600">L3/L4 Distance Range:</span>
						<span class="text-sm font-medium text-gray-900">
							{selectedScenario.expected_distance_range[0]} - {selectedScenario
								.expected_distance_range[1]}
						</span>
					</div>
					{#if selectedScenario.metadata.expected_behavior}
						<p class="text-xs text-gray-600 italic">
							{selectedScenario.metadata.expected_behavior}
						</p>
					{/if}
				</div>
			</div>

			<!-- Context -->
			<div>
				<label class="text-xs font-medium text-gray-500 block mb-1">Context:</label>
				<p class="text-sm text-gray-700">{selectedScenario.context}</p>
			</div>

			<!-- Theory -->
			{#if selectedScenario.metadata.theory}
				<div class="bg-indigo-50 p-3 rounded border border-indigo-100">
					<label class="text-xs font-medium text-indigo-700 block mb-1">Theory:</label>
					<p class="text-sm text-indigo-900">{selectedScenario.metadata.theory}</p>
				</div>
			{/if}

			<!-- Load button -->
			<button
				on:click={handleLoadScenario}
				class="w-full mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors font-medium"
			>
				Load This Scenario
			</button>
		</div>
	{/if}
</div>

<style>
	.scenario-selector {
		max-width: 100%;
	}

	select {
		cursor: pointer;
	}

	select:disabled {
		cursor: not-allowed;
	}
</style>
