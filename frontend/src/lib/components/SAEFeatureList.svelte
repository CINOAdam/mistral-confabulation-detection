<script lang="ts">
	import type { SAEFeature } from '$lib/types';
	import FeatureDetailModal from './FeatureDetailModal.svelte';

	export let features: SAEFeature[];
	export let maxFeatures = 10;

	let selectedFeature: SAEFeature | null = null;
	let showModal = false;

	// Sort by activation value (descending)
	$: sortedFeatures = [...features]
		.sort((a, b) => b.activation - a.activation)
		.slice(0, maxFeatures);

	// Calculate max activation for scaling bars
	$: maxActivation = sortedFeatures.length > 0
		? Math.max(...sortedFeatures.map(f => f.activation))
		: 1;

	function handleFeatureClick(feature: SAEFeature) {
		selectedFeature = feature;
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		selectedFeature = null;
	}

	function getBarWidth(activation: number): number {
		return (activation / maxActivation) * 100;
	}

	function getBarColor(activation: number): string {
		// Color gradient based on activation strength
		const ratio = activation / maxActivation;
		if (ratio > 0.7) return 'bg-red-500';
		if (ratio > 0.4) return 'bg-amber-500';
		return 'bg-blue-500';
	}
</script>

<div class="sae-feature-list">
	<div class="mb-3">
		<h3 class="text-sm font-bold text-gray-700 uppercase tracking-wide">
			Top SAE Features (Layer 30)
		</h3>
		<p class="text-xs text-gray-500 mt-1">
			Showing {sortedFeatures.length} most active features
		</p>
	</div>

	{#if sortedFeatures.length === 0}
		<div class="text-center text-gray-400 py-8">
			No SAE features detected
		</div>
	{:else}
		<div class="space-y-2">
			{#each sortedFeatures as feature (feature.idx)}
				<button
					class="w-full text-left border border-gray-200 rounded-lg p-3 hover:border-blue-400 hover:bg-blue-50 transition-all cursor-pointer"
					on:click={() => handleFeatureClick(feature)}
					aria-label={`Feature ${feature.idx} with activation ${feature.activation.toFixed(3)}`}
				>
					<div class="flex justify-between items-center mb-2">
						<div class="font-mono text-sm font-bold text-gray-800">
							Feature {feature.idx}
						</div>
						<div class="font-mono text-sm text-gray-600">
							{feature.activation.toFixed(3)}
						</div>
					</div>

					<!-- Activation strength bar -->
					<div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
						<div
							class={`h-full ${getBarColor(feature.activation)} transition-all duration-300`}
							style={`width: ${getBarWidth(feature.activation)}%`}
						></div>
					</div>

					{#if feature.description}
						<div class="text-xs text-gray-500 mt-2">
							{feature.description}
						</div>
					{/if}
				</button>
			{/each}
		</div>
	{/if}
</div>

<!-- Feature detail modal -->
{#if showModal && selectedFeature}
	<FeatureDetailModal feature={selectedFeature} onClose={closeModal} />
{/if}

<style>
	.sae-feature-list {
		max-height: 400px;
		overflow-y: auto;
	}

	.sae-feature-list::-webkit-scrollbar {
		width: 8px;
	}

	.sae-feature-list::-webkit-scrollbar-track {
		background: #f1f1f1;
		border-radius: 4px;
	}

	.sae-feature-list::-webkit-scrollbar-thumb {
		background: #888;
		border-radius: 4px;
	}

	.sae-feature-list::-webkit-scrollbar-thumb:hover {
		background: #555;
	}
</style>
