<script lang="ts">
	import { getFeatureAnnotation } from '$lib/api';
	import type { SAEFeature } from '$lib/types';

	export let feature: SAEFeature | null = null;
	export let onClose: () => void;

	let loading = false;
	let error: string | null = null;
	let detailedAnnotation: {
		idx: number;
		description: string;
		layer: number;
		neuronpedia_url: string;
	} | null = null;

	// Fetch detailed annotation when feature changes
	$: if (feature) {
		fetchAnnotation(feature.idx);
	}

	async function fetchAnnotation(featureIdx: number) {
		loading = true;
		error = null;
		detailedAnnotation = null;

		try {
			detailedAnnotation = await getFeatureAnnotation(featureIdx);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load annotation';
			console.error('Error fetching annotation:', e);
		} finally {
			loading = false;
		}
	}

	function handleBackdropClick(event: MouseEvent) {
		if (event.target === event.currentTarget) {
			onClose();
		}
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			onClose();
		}
	}
</script>

<svelte:window on:keydown={handleKeyDown} />

{#if feature}
	<div
		class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
		on:click={handleBackdropClick}
		role="dialog"
		aria-modal="true"
		aria-labelledby="modal-title"
	>
		<div
			class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
			on:click|stopPropagation
		>
			<!-- Header -->
			<div class="border-b border-gray-200 px-6 py-4 flex justify-between items-center sticky top-0 bg-white">
				<h2 id="modal-title" class="text-xl font-bold text-gray-800">
					Feature {feature.idx}
				</h2>
				<button
					class="text-gray-400 hover:text-gray-600 transition-colors"
					on:click={onClose}
					aria-label="Close modal"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<!-- Content -->
			<div class="px-6 py-4 space-y-4">
				<!-- Activation value -->
				<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
					<div class="text-sm text-blue-700 font-semibold mb-1">Activation Value</div>
					<div class="text-2xl font-mono font-bold text-blue-900">
						{feature.activation.toFixed(4)}
					</div>
				</div>

				<!-- Loading state -->
				{#if loading}
					<div class="flex items-center justify-center py-8">
						<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
						<span class="ml-3 text-gray-600">Loading annotation...</span>
					</div>
				{/if}

				<!-- Error state -->
				{#if error}
					<div class="bg-red-50 border border-red-200 rounded-lg p-4">
						<div class="flex items-start">
							<svg class="w-5 h-5 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
							</svg>
							<div class="ml-3">
								<h3 class="text-sm font-medium text-red-800">Error loading annotation</h3>
								<p class="text-sm text-red-700 mt-1">{error}</p>
							</div>
						</div>
					</div>
				{/if}

				<!-- Annotation content -->
				{#if detailedAnnotation && !loading}
					<div class="space-y-4">
						<!-- Description -->
						<div>
							<h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">
								Description
							</h3>
							<p class="text-gray-800 leading-relaxed">
								{detailedAnnotation.description}
							</p>
						</div>

						<!-- Layer info -->
						<div class="flex items-center text-sm text-gray-600">
							<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z" />
							</svg>
							Layer {detailedAnnotation.layer}
						</div>

						<!-- Neuronpedia link -->
						<div class="pt-4 border-t border-gray-200">
							<a
								href={detailedAnnotation.neuronpedia_url}
								target="_blank"
								rel="noopener noreferrer"
								class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
							>
								<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
								</svg>
								Explore on Neuronpedia
							</a>
							<p class="text-xs text-gray-500 mt-2">
								View detailed activation examples and community annotations
							</p>
						</div>
					</div>
				{/if}

				<!-- Fallback basic description -->
				{#if !loading && !error && !detailedAnnotation && feature.description}
					<div>
						<h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">
							Description
						</h3>
						<p class="text-gray-800">
							{feature.description}
						</p>
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="border-t border-gray-200 px-6 py-4 bg-gray-50">
				<button
					class="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
					on:click={onClose}
				>
					Close
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Smooth scroll for modal content */
	.overflow-y-auto {
		scrollbar-width: thin;
		scrollbar-color: #cbd5e0 #f7fafc;
	}

	.overflow-y-auto::-webkit-scrollbar {
		width: 8px;
	}

	.overflow-y-auto::-webkit-scrollbar-track {
		background: #f7fafc;
	}

	.overflow-y-auto::-webkit-scrollbar-thumb {
		background-color: #cbd5e0;
		border-radius: 4px;
	}

	.overflow-y-auto::-webkit-scrollbar-thumb:hover {
		background-color: #a0aec0;
	}
</style>
