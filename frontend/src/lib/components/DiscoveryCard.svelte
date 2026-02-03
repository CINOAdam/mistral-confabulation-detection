<script lang="ts">
	export let discovery: {
		id: string;
		title: string;
		subtitle: string;
		icon: string;
		problem: string;
		finding: string;
		evidence: Array<{
			type: string;
			label: string;
			value: string;
			description: string;
		}>;
		mechanism: string[];
		implications: string[];
		keyFeatures: Array<{
			idx: number;
			description: string;
		}>;
		scenarios: string[];
		visualType: string;
	};

	let expanded = false;

	function toggleExpanded() {
		expanded = !expanded;
	}

	// Generate visualization based on visual type
	function getVisualization(type: string) {
		switch (type) {
			case 'distance-comparison':
				return {
					title: 'L3/L4 Distance Distribution',
					description: 'Honest responses cluster below 50, deceptive above'
				};
			case 'mechanism-comparison':
				return {
					title: 'Shared Neural Pathways',
					description: 'Deception and refusal activate same circuits'
				};
			case 'bimodal-distribution':
				return {
					title: 'Bimodal Processing Regimes',
					description: 'Sharp threshold separates two distinct modes'
				};
			default:
				return { title: 'Visualization', description: '' };
		}
	}

	$: visualization = getVisualization(discovery.visualType);
</script>

<div class="discovery-card card" id={discovery.id}>
	<!-- Header -->
	<div class="flex items-start justify-between mb-6">
		<div class="flex items-start gap-4">
			<div class="text-4xl">{discovery.icon}</div>
			<div>
				<h3 class="text-2xl font-bold text-neutral-900 mb-2">{discovery.title}</h3>
				<p class="text-lg text-neutral-600">{discovery.subtitle}</p>
			</div>
		</div>
		<div class="flex items-center gap-2">
			<a
				href="/?discovery={discovery.id}"
				class="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
			>
				Try Demo
			</a>
		</div>
	</div>

	<!-- Problem Statement -->
	<div class="mb-6">
		<h4 class="text-sm font-semibold text-neutral-500 uppercase tracking-wide mb-2">
			Problem
		</h4>
		<p class="text-research">{discovery.problem}</p>
	</div>

	<!-- Key Finding -->
	<div class="bg-accent-50 border-l-4 border-accent-500 p-4 rounded-r-lg mb-6">
		<h4 class="text-sm font-semibold text-accent-900 uppercase tracking-wide mb-2">
			Key Finding
		</h4>
		<p class="text-neutral-900 font-medium leading-relaxed">{discovery.finding}</p>
	</div>

	<!-- Evidence Metrics -->
	<div class="mb-6">
		<h4 class="text-sm font-semibold text-neutral-500 uppercase tracking-wide mb-3">
			Evidence
		</h4>
		<div class="grid md:grid-cols-3 gap-4">
			{#each discovery.evidence as metric}
				<div class="metric">
					<div class="metric-value">{metric.value}</div>
					<div class="metric-label">{metric.label}</div>
					<p class="text-xs text-neutral-600 mt-2">{metric.description}</p>
				</div>
			{/each}
		</div>
	</div>

	<!-- Visualization -->
	<div class="mb-6">
		<h4 class="text-sm font-semibold text-neutral-500 uppercase tracking-wide mb-3">
			{visualization.title}
		</h4>
		<div class="viz-container">
			{#if discovery.visualType === 'distance-comparison'}
				<!-- Distance comparison chart -->
				<div class="flex items-end justify-center gap-8 h-48">
					<!-- Honest bar -->
					<div class="flex flex-col items-center">
						<div class="relative w-32">
							<div class="bg-green-500 rounded-t-lg h-16 flex items-center justify-center">
								<span class="text-white font-bold text-2xl">&lt;50</span>
							</div>
							<div class="absolute -top-8 left-1/2 -translate-x-1/2 text-xs text-neutral-600 whitespace-nowrap">
								Mean: 1.8
							</div>
						</div>
						<div class="mt-2 text-sm font-medium text-neutral-700">Honest</div>
						<div class="text-xs text-neutral-500">Preserved</div>
					</div>
					<!-- Deceptive bar -->
					<div class="flex flex-col items-center">
						<div class="relative w-32">
							<div class="bg-red-500 rounded-t-lg h-40 flex items-center justify-center">
								<span class="text-white font-bold text-2xl">≥50</span>
							</div>
							<div class="absolute -top-8 left-1/2 -translate-x-1/2 text-xs text-neutral-600 whitespace-nowrap">
								Mean: 50-200
							</div>
						</div>
						<div class="mt-2 text-sm font-medium text-neutral-700">Deceptive</div>
						<div class="text-xs text-neutral-500">Transformed</div>
					</div>
				</div>
				<p class="text-caption text-center mt-4">{visualization.description}</p>
			{:else if discovery.visualType === 'mechanism-comparison'}
				<!-- Mechanism comparison diagram -->
				<div class="flex items-center justify-center py-8">
					<div class="flex items-center gap-8">
						<!-- Deception path -->
						<div class="flex flex-col items-center">
							<div class="w-32 h-24 bg-red-100 border-2 border-red-500 rounded-lg flex items-center justify-center p-2">
								<div class="text-center">
									<div class="font-bold text-red-900 text-sm">Deception</div>
									<div class="text-xs text-red-700">L3→L4</div>
								</div>
							</div>
							<div class="text-xs text-neutral-600 mt-2">Distance ≥50</div>
						</div>

						<!-- Shared pathway arrow -->
						<div class="flex flex-col items-center">
							<div class="text-3xl text-accent-500">⇄</div>
							<div class="text-xs font-bold text-accent-700">80% overlap</div>
						</div>

						<!-- Refusal path -->
						<div class="flex flex-col items-center">
							<div class="w-32 h-24 bg-blue-100 border-2 border-blue-500 rounded-lg flex items-center justify-center p-2">
								<div class="text-center">
									<div class="font-bold text-blue-900 text-sm">Refusal</div>
									<div class="text-xs text-blue-700">L3→L4</div>
								</div>
							</div>
							<div class="text-xs text-neutral-600 mt-2">Distance ≥50</div>
						</div>
					</div>
				</div>
				<p class="text-caption text-center">{visualization.description}</p>
			{:else if discovery.visualType === 'bimodal-distribution'}
				<!-- Bimodal distribution chart -->
				<div class="flex items-center justify-center py-8">
					<div class="relative w-full max-w-xl">
						<!-- Y-axis -->
						<div class="absolute left-0 top-0 bottom-0 w-px bg-neutral-300"></div>
						<!-- X-axis -->
						<div class="absolute left-0 right-0 bottom-8 h-px bg-neutral-300"></div>

						<!-- Distribution peaks -->
						<div class="flex items-end justify-between h-48 px-8">
							<!-- Preserved peak -->
							<div class="flex flex-col items-center w-1/3">
								<div class="bg-green-500 rounded-t-lg w-full h-32 relative">
									<div class="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-bold text-green-700">
										~1.8
									</div>
								</div>
								<div class="mt-2 text-sm font-medium">Preserved</div>
							</div>

							<!-- Gap -->
							<div class="w-1/3 flex items-end justify-center">
								<div class="text-2xl font-bold text-neutral-400 pb-4">⋯</div>
							</div>

							<!-- Transformed peak -->
							<div class="flex flex-col items-center w-1/3">
								<div class="bg-red-500 rounded-t-lg w-full h-36 relative">
									<div class="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-bold text-red-700">
										50-200
									</div>
								</div>
								<div class="mt-2 text-sm font-medium">Transformed</div>
							</div>
						</div>

						<!-- Threshold line -->
						<div class="absolute left-1/2 top-0 bottom-8 w-0.5 bg-accent-500 -translate-x-1/2">
							<div class="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap">
								<div class="text-xs font-bold text-accent-700 bg-white px-2">
									Threshold = 50
								</div>
							</div>
						</div>

						<!-- Axis labels -->
						<div class="absolute -bottom-2 left-1/2 -translate-x-1/2 text-xs text-neutral-600">
							L3/L4 Distance (×100)
						</div>
					</div>
				</div>
				<p class="text-caption text-center">{visualization.description}</p>
			{/if}
		</div>
	</div>

	<!-- Mechanism (expandable) -->
	<div class="mb-6">
		<button
			class="w-full flex items-center justify-between text-left mb-3 hover:text-primary-600 transition-colors"
			on:click={toggleExpanded}
		>
			<h4 class="text-sm font-semibold text-neutral-500 uppercase tracking-wide">
				Mechanism Details
			</h4>
			<svg
				class="w-5 h-5 transform transition-transform {expanded ? 'rotate-180' : ''}"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		{#if expanded}
			<div class="bg-neutral-50 rounded-lg p-4 space-y-2">
				{#each discovery.mechanism as step, i}
					<div class="flex items-start gap-3">
						<div class="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
							{i + 1}
						</div>
						<p class="text-sm text-research flex-1">{step}</p>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Key SAE Features -->
	{#if expanded}
		<div class="mb-6">
			<h4 class="text-sm font-semibold text-neutral-500 uppercase tracking-wide mb-3">
				Key SAE Features
			</h4>
			<div class="bg-neutral-50 rounded-lg p-4">
				<table class="w-full text-sm">
					<thead>
						<tr class="border-b border-neutral-200">
							<th class="text-left py-2 font-semibold text-neutral-700">Feature ID</th>
							<th class="text-left py-2 font-semibold text-neutral-700">Description</th>
						</tr>
					</thead>
					<tbody>
						{#each discovery.keyFeatures as feature}
							<tr class="border-b border-neutral-100">
								<td class="py-2 font-mono text-primary-600">{feature.idx}</td>
								<td class="py-2 text-neutral-700">{feature.description}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}

	<!-- Implications -->
	<div class="mb-6">
		<h4 class="text-sm font-semibold text-neutral-500 uppercase tracking-wide mb-3">
			Implications for AI Safety
		</h4>
		<ul class="space-y-2">
			{#each discovery.implications as implication}
				<li class="flex items-start gap-2 text-research">
					<span class="text-accent-600 font-bold">→</span>
					<span>{implication}</span>
				</li>
			{/each}
		</ul>
	</div>

	<!-- Try It Yourself -->
	<div class="border-t border-neutral-200 pt-6">
		<div class="flex items-center justify-between">
			<div>
				<h4 class="font-semibold text-neutral-900 mb-1">Try This Discovery</h4>
				<p class="text-sm text-neutral-600">
					Test with {discovery.scenarios.length} pre-configured scenarios
				</p>
			</div>
			<a
				href="/?discovery={discovery.id}"
				class="px-6 py-2 bg-accent-500 text-white font-medium rounded-lg hover:bg-accent-600 transition-colors"
			>
				Launch Demo →
			</a>
		</div>
	</div>
</div>

<style>
	.discovery-card {
		scroll-margin-top: 100px;
	}
</style>
