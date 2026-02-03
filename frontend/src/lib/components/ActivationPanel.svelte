<script lang="ts">
	import type { ActivationData } from '$lib/types';
	import SAEFeatureList from './SAEFeatureList.svelte';
	import RegimeIndicator from './RegimeIndicator.svelte';

	export let activations: ActivationData | null;

	let earlyLayersExpanded = true;
	let lateLayerExpanded = true;

	function toggleEarlyLayers() {
		earlyLayersExpanded = !earlyLayersExpanded;
	}

	function toggleLateLayer() {
		lateLayerExpanded = !lateLayerExpanded;
	}

	// Calculate color intensity for heatmap
	function getHeatmapColor(activation: number, maxVal: number): string {
		const intensity = Math.min(activation / maxVal, 1);
		const red = Math.round(255 * intensity);
		const blue = Math.round(255 * (1 - intensity));
		return `rgb(${red}, 100, ${blue})`;
	}
</script>

<div class="activation-panel bg-white border-l border-gray-200 h-full overflow-y-auto">
	{#if !activations}
		<div class="flex items-center justify-center h-full text-gray-400">
			<div class="text-center">
				<svg
					class="w-16 h-16 mx-auto mb-4 opacity-50"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
					/>
				</svg>
				<p class="text-sm font-medium">No activation data</p>
				<p class="text-xs mt-1">Send a message to see neural activations</p>
			</div>
		</div>
	{:else}
		<div class="p-4 space-y-4">
			<!-- Regime Classification -->
			<RegimeIndicator
				regime={activations.regime_classification}
				distance={activations.regime_distance}
			/>

			<!-- Early Layers (1-5) -->
			<div class="border border-gray-200 rounded-lg overflow-hidden">
				<button
					class="w-full flex items-center justify-between bg-gray-100 px-4 py-3 hover:bg-gray-200 transition-colors"
					on:click={toggleEarlyLayers}
				>
					<div>
						<h3 class="text-sm font-bold text-gray-800">Early Layers (1-5)</h3>
						<p class="text-xs text-gray-500">Initial token processing</p>
					</div>
					<svg
						class="w-5 h-5 text-gray-600 transition-transform {earlyLayersExpanded
							? 'rotate-180'
							: ''}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>

				{#if earlyLayersExpanded}
					<div class="p-4 space-y-3">
						{#each Object.entries(activations.early_activations) as [layerNum, layerActivations]}
							<div class="text-xs">
								<div class="flex justify-between items-center mb-2">
									<span class="font-bold text-gray-700">Layer {layerNum}</span>
									<div class="text-gray-500">
										<span>Dim: {layerActivations.length}</span>
										<span class="ml-2">Mean: {(layerActivations.reduce((a, b) => a + Math.abs(b), 0) / layerActivations.length).toFixed(3)}</span>
										<span class="ml-2">Max: {Math.max(...layerActivations.map(Math.abs)).toFixed(3)}</span>
									</div>
								</div>

								<!-- Simple activation distribution bar -->
								<div class="h-8 bg-gray-100 rounded relative overflow-hidden">
									<div
										class="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 opacity-60"
										style="width: {Math.min(100, (layerActivations.filter(x => Math.abs(x) > 0.1).length / layerActivations.length) * 100)}%"
									></div>
									<div class="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-700">
										{layerActivations.filter(x => Math.abs(x) > 0.1).length} / {layerActivations.length} active (|x| > 0.1)
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Late Layer (30) with SAE Features -->
			<div class="border border-gray-200 rounded-lg overflow-hidden">
				<button
					class="w-full flex items-center justify-between bg-gray-100 px-4 py-3 hover:bg-gray-200 transition-colors"
					on:click={toggleLateLayer}
				>
					<div>
						<h3 class="text-sm font-bold text-gray-800">Layer 30 - SAE Features</h3>
						<p class="text-xs text-gray-500">Strategic processing layer</p>
					</div>
					<svg
						class="w-5 h-5 text-gray-600 transition-transform {lateLayerExpanded
							? 'rotate-180'
							: ''}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>

				{#if lateLayerExpanded}
					<div class="p-4">
						<div class="mb-3 text-xs space-y-1 bg-blue-50 p-3 rounded">
							<div class="flex justify-between">
								<span class="text-gray-600">Dimensions:</span>
								<span class="font-mono font-bold">{activations.late_activations.length}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Mean Activation:</span>
								<span class="font-mono font-bold">{(activations.late_activations.reduce((a, b) => a + Math.abs(b), 0) / activations.late_activations.length).toFixed(3)}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Max Activation:</span>
								<span class="font-mono font-bold">{Math.max(...activations.late_activations.map(Math.abs)).toFixed(3)}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Active SAE Features:</span>
								<span class="font-mono font-bold">{activations.sae_features.length}</span>
							</div>
						</div>

						<SAEFeatureList features={activations.sae_features} maxFeatures={10} />
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.activation-panel {
		min-height: 100vh;
	}

	.activation-panel::-webkit-scrollbar {
		width: 10px;
	}

	.activation-panel::-webkit-scrollbar-track {
		background: #f9fafb;
	}

	.activation-panel::-webkit-scrollbar-thumb {
		background: #d1d5db;
		border-radius: 5px;
	}

	.activation-panel::-webkit-scrollbar-thumb:hover {
		background: #9ca3af;
	}
</style>
