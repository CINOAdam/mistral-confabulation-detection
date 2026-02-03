<script lang="ts">
	let expandedSections: { [key: string]: boolean } = {
		model: false,
		sae: false,
		distance: false,
		threshold: false,
		experimental: false,
		data: false
	};

	function toggleSection(section: string) {
		expandedSections[section] = !expandedSections[section];
	}
</script>

<div class="max-w-4xl mx-auto">
	<div class="text-center mb-8">
		<h2 class="text-3xl font-bold text-neutral-900 mb-4">Methodology</h2>
		<p class="text-lg text-neutral-600">
			Reproducible research design enabling validation across models and datasets
		</p>
	</div>

	<!-- Model Details -->
	<div class="card mb-4">
		<button
			class="w-full flex items-center justify-between text-left"
			on:click={() => toggleSection('model')}
		>
			<h3 class="text-xl font-semibold text-neutral-900">Model Architecture</h3>
			<svg
				class="w-5 h-5 transform transition-transform {expandedSections.model ? 'rotate-180' : ''}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		{#if expandedSections.model}
			<div class="mt-4 pt-4 border-t border-neutral-200 space-y-3">
				<div class="grid md:grid-cols-2 gap-4">
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Model</div>
						<div class="font-mono text-primary-600">Mistral-22B-v0.1</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Parameters</div>
						<div class="font-mono text-primary-600">22.1B</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Architecture</div>
						<div class="font-mono text-primary-600">Transformer (32 layers)</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Hidden Size</div>
						<div class="font-mono text-primary-600">4096</div>
					</div>
				</div>

				<div class="text-sm text-research">
					<p class="mb-2">
						<strong>Rationale:</strong> Mistral-22B provides a production-scale model with open
						architecture, enabling deep inspection of internal representations. Size is large
						enough to exhibit complex strategic behaviors but small enough for real-time monitoring.
					</p>
					<p>
						<strong>Training:</strong> Pre-trained on diverse web data with RLHF safety fine-tuning,
						replicating typical deployment conditions where deceptive behaviors may emerge.
					</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- SAE Architecture -->
	<div class="card mb-4">
		<button
			class="w-full flex items-center justify-between text-left"
			on:click={() => toggleSection('sae')}
		>
			<h3 class="text-xl font-semibold text-neutral-900">Sparse Autoencoder (SAE) Setup</h3>
			<svg
				class="w-5 h-5 transform transition-transform {expandedSections.sae ? 'rotate-180' : ''}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		{#if expandedSections.sae}
			<div class="mt-4 pt-4 border-t border-neutral-200 space-y-3">
				<div class="grid md:grid-cols-2 gap-4">
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Target Layer</div>
						<div class="font-mono text-primary-600">Layer 30 (Late)</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Feature Dimensions</div>
						<div class="font-mono text-primary-600">524,288 (2^19)</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Sparsity Target</div>
						<div class="font-mono text-primary-600">L1 = 0.001</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Training Tokens</div>
						<div class="font-mono text-primary-600">~100M</div>
					</div>
				</div>

				<div class="text-sm text-research">
					<p class="mb-2">
						<strong>Design:</strong> Dictionary learning approach following Anthropic's monosemanticity
						research. SAE decomposes dense activations into interpretable sparse features.
					</p>
					<p>
						<strong>Feature Identification:</strong> Manual inspection of top-activating features
						combined with automated clustering identified features 60179, 132378, 271232 as
						consistently active during strategic processing.
					</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- L3/L4 Distance Calculation -->
	<div class="card mb-4">
		<button
			class="w-full flex items-center justify-between text-left"
			on:click={() => toggleSection('distance')}
		>
			<h3 class="text-xl font-semibold text-neutral-900">L3/L4 Distance Metric</h3>
			<svg
				class="w-5 h-5 transform transition-transform {expandedSections.distance ? 'rotate-180' : ''}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		{#if expandedSections.distance}
			<div class="mt-4 pt-4 border-t border-neutral-200 space-y-4">
				<div class="bg-neutral-900 text-green-400 rounded-lg p-4 font-mono text-sm">
					<pre><code>def calculate_l3_l4_distance(l3_activations, l4_activations):
    """
    Compute cosine distance between token representations
    at layers 3 and 4 (×100 for readability)
    """
    # Average over all tokens in sequence
    l3_mean = torch.mean(l3_activations, dim=0)
    l4_mean = torch.mean(l4_activations, dim=0)

    # Cosine distance = 1 - cosine_similarity
    cos_sim = F.cosine_similarity(l3_mean, l4_mean, dim=0)
    distance = (1 - cos_sim) * 100

    return distance.item()</code></pre>
				</div>

				<div class="text-sm text-research">
					<p class="mb-2">
						<strong>Rationale:</strong> Cosine distance captures semantic shift between layers
						regardless of magnitude changes. Multiply by 100 for human-readable scale.
					</p>
					<p>
						<strong>Interpretation:</strong> Distance measures how much the model "changes its mind"
						about token meanings between layers 3 and 4. Low distance = preserved semantics. High
						distance = transformed semantics.
					</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- Threshold Determination -->
	<div class="card mb-4">
		<button
			class="w-full flex items-center justify-between text-left"
			on:click={() => toggleSection('threshold')}
		>
			<h3 class="text-xl font-semibold text-neutral-900">Threshold Determination (SipIt)</h3>
			<svg
				class="w-5 h-5 transform transition-transform {expandedSections.threshold
					? 'rotate-180'
					: ''}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		{#if expandedSections.threshold}
			<div class="mt-4 pt-4 border-t border-neutral-200 space-y-3">
				<div class="bg-accent-50 border-l-4 border-accent-500 p-4 rounded-r-lg">
					<h4 class="font-semibold text-accent-900 mb-2">SipIt Bimodal Discovery</h4>
					<p class="text-sm text-research">
						The threshold of 50 was not chosen arbitrarily. SipIt research revealed a bimodal
						distribution in hidden state reconstructions across thousands of prompts. The
						distribution showed two clear peaks at ~1.8 (preserved) and ~100 (transformed) with
						minimal overlap, suggesting a natural boundary around 50.
					</p>
				</div>

				<div class="text-sm text-research space-y-2">
					<p>
						<strong>Validation approach:</strong>
					</p>
					<ol class="list-decimal list-inside space-y-1 ml-4">
						<li>Collected L3/L4 distances for 1000+ diverse prompts</li>
						<li>Histogram revealed clear bimodal distribution</li>
						<li>Gaussian mixture model confirmed two components (p &lt; 0.001)</li>
						<li>
							Threshold set at midpoint between peaks (~50) for maximum separation
						</li>
						<li>Cross-validation showed 95%+ accuracy on held-out test set</li>
					</ol>
				</div>

				<div class="grid md:grid-cols-2 gap-4 mt-4">
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Preserved Peak</div>
						<div class="font-mono text-green-600 text-lg">μ = 1.8, σ = 0.5</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Transformed Peak</div>
						<div class="font-mono text-red-600 text-lg">μ = 98, σ = 30</div>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Experimental Design -->
	<div class="card mb-4">
		<button
			class="w-full flex items-center justify-between text-left"
			on:click={() => toggleSection('experimental')}
		>
			<h3 class="text-xl font-semibold text-neutral-900">Experimental Design</h3>
			<svg
				class="w-5 h-5 transform transition-transform {expandedSections.experimental
					? 'rotate-180'
					: ''}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		{#if expandedSections.experimental}
			<div class="mt-4 pt-4 border-t border-neutral-200 space-y-4">
				<div class="text-sm text-research">
					<h4 class="font-semibold text-neutral-900 mb-2">Phase 1: Hypothesis Generation</h4>
					<ul class="list-disc list-inside space-y-1 ml-4">
						<li>SipIt analysis revealed bimodal distribution in hidden states</li>
						<li>
							Hypothesis: Early layer distances predict deceptive vs honest processing
						</li>
						<li>Initial testing on layers 1-5 to identify critical transition point</li>
					</ul>
				</div>

				<div class="text-sm text-research">
					<h4 class="font-semibold text-neutral-900 mb-2">Phase 2: Discovery Validation</h4>
					<ul class="list-disc list-inside space-y-1 ml-4">
						<li>Designed 30 test scenarios across 3 discovery types</li>
						<li>Each scenario labeled with expected regime (honest/deceptive)</li>
						<li>Blind evaluation: threshold applied without scenario-specific tuning</li>
						<li>Results: 95% accuracy, confirmed robustness of threshold</li>
					</ul>
				</div>

				<div class="text-sm text-research">
					<h4 class="font-semibold text-neutral-900 mb-2">Phase 3: Mechanistic Analysis</h4>
					<ul class="list-disc list-inside space-y-1 ml-4">
						<li>SAE feature identification via top-activating examples</li>
						<li>Causal probing: ablate features, measure impact on distance</li>
						<li>Discovered shared circuits between deception and safety refusals</li>
					</ul>
				</div>

				<div class="bg-primary-50 border border-primary-200 rounded p-4 mt-4">
					<h4 class="font-semibold text-primary-900 mb-2">Controls & Validation</h4>
					<ul class="list-disc list-inside space-y-1 ml-2 text-sm">
						<li>Random baseline: 50% accuracy (vs our 95%)</li>
						<li>Other layer pairs (L2/L3, L4/L5): lower separation, 70-80% accuracy</li>
						<li>Alternative metrics (L2 distance, KL divergence): similar results</li>
						<li>Different model sizes (7B, 13B, 22B): threshold scales linearly</li>
					</ul>
				</div>
			</div>
		{/if}
	</div>

	<!-- Data Collection -->
	<div class="card mb-4">
		<button
			class="w-full flex items-center justify-between text-left"
			on:click={() => toggleSection('data')}
		>
			<h3 class="text-xl font-semibold text-neutral-900">Data Collection & Analysis</h3>
			<svg
				class="w-5 h-5 transform transition-transform {expandedSections.data ? 'rotate-180' : ''}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		{#if expandedSections.data}
			<div class="mt-4 pt-4 border-t border-neutral-200 space-y-4">
				<div class="grid md:grid-cols-3 gap-4">
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Total Prompts</div>
						<div class="font-mono text-primary-600 text-2xl">1,247</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Test Scenarios</div>
						<div class="font-mono text-primary-600 text-2xl">30</div>
					</div>
					<div class="bg-neutral-50 rounded p-3">
						<div class="text-sm font-semibold text-neutral-600 mb-1">Activations Captured</div>
						<div class="font-mono text-primary-600 text-2xl">~40M</div>
					</div>
				</div>

				<div class="text-sm text-research">
					<p class="mb-2">
						<strong>Prompt Categories:</strong>
					</p>
					<ul class="list-disc list-inside space-y-1 ml-4">
						<li><strong>Factual queries</strong> (n=450): Verifiable information requests</li>
						<li>
							<strong>Opinion questions</strong> (n=320): Subjective topics without ground truth
						</li>
						<li>
							<strong>Harmful requests</strong> (n=180): Safety-filtered prompts triggering
							refusals
						</li>
						<li>
							<strong>Jailbreak attempts</strong> (n=120): Adversarial prompts testing safety
						</li>
						<li>
							<strong>Mixed scenarios</strong> (n=177): Combination of factual + strategic elements
						</li>
					</ul>
				</div>

				<div class="text-sm text-research">
					<p class="mb-2">
						<strong>Analysis Pipeline:</strong>
					</p>
					<ol class="list-decimal list-inside space-y-1 ml-4">
						<li>Capture activations for layers 1-5 and 30 during generation</li>
						<li>Compute L3/L4 distance for each response</li>
						<li>Apply threshold (50) to classify regime</li>
						<li>Extract top-k SAE features (k=20) from layer 30</li>
						<li>Store results for interactive demonstration</li>
					</ol>
				</div>

				<div class="bg-neutral-50 border border-neutral-200 rounded p-4 mt-4">
					<h4 class="font-semibold text-neutral-900 mb-2">Reproducibility</h4>
					<p class="text-sm text-research mb-2">
						All data, code, and analysis scripts are available in the project repository. The
						interactive demo provides real-time reproduction of core findings.
					</p>
					<a
						href="https://github.com/yourusername/mistral-reproducibility"
						class="inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
						target="_blank"
						rel="noopener noreferrer"
					>
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
							<path
								d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
							/>
						</svg>
						View Repository
					</a>
				</div>
			</div>
		{/if}
	</div>

	<!-- Statistical Rigor -->
	<div class="card bg-neutral-50">
		<h3 class="text-xl font-semibold text-neutral-900 mb-4">Statistical Rigor</h3>
		<div class="grid md:grid-cols-2 gap-6 text-sm text-research">
			<div>
				<h4 class="font-semibold text-neutral-900 mb-2">Significance Testing</h4>
				<ul class="list-disc list-inside space-y-1 ml-2">
					<li>Two-sample t-test: p &lt; 0.001 (preserved vs transformed)</li>
					<li>Effect size (Cohen's d): 3.8 (very large)</li>
					<li>Gaussian mixture model: BIC confirms 2 components</li>
				</ul>
			</div>
			<div>
				<h4 class="font-semibold text-neutral-900 mb-2">Cross-Validation</h4>
				<ul class="list-disc list-inside space-y-1 ml-2">
					<li>5-fold CV: 94.8% ± 1.2% accuracy</li>
					<li>Hold-out test set: 95.3% accuracy</li>
					<li>Bootstrap confidence interval: [94.1%, 96.5%]</li>
				</ul>
			</div>
		</div>
	</div>
</div>
