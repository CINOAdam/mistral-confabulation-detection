<script lang="ts">
	export let timeline: Array<{
		date: string;
		event: string;
		description: string;
		milestone?: boolean;
		current?: boolean;
	}>;
</script>

<div class="max-w-4xl mx-auto">
	<div class="relative">
		<!-- Vertical line -->
		<div class="absolute left-8 top-0 bottom-0 w-0.5 bg-neutral-300"></div>

		<!-- Timeline items -->
		<div class="space-y-8">
			{#each timeline as item, i}
				<div class="relative pl-20">
					<!-- Dot -->
					<div
						class="absolute left-6 top-1 w-5 h-5 rounded-full border-4 {item.current
							? 'bg-accent-500 border-accent-600 ring-4 ring-accent-200'
							: item.milestone
								? 'bg-primary-500 border-primary-600'
								: 'bg-white border-neutral-400'}"
					></div>

					<!-- Date badge -->
					<div
						class="absolute left-0 top-0 text-xs font-mono font-semibold {item.current
							? 'text-accent-700'
							: item.milestone
								? 'text-primary-700'
								: 'text-neutral-600'} w-16 -ml-2"
					>
						{item.date}
					</div>

					<!-- Content -->
					<div
						class="card {item.current
							? 'border-accent-500 bg-accent-50'
							: item.milestone
								? 'border-primary-300 bg-primary-50'
								: 'bg-white'}"
					>
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<h3
									class="text-lg font-semibold mb-1 {item.current
										? 'text-accent-900'
										: item.milestone
											? 'text-primary-900'
											: 'text-neutral-900'}"
								>
									{item.event}
									{#if item.current}
										<span
											class="ml-2 text-xs font-medium px-2 py-1 bg-accent-200 text-accent-800 rounded"
										>
											Current
										</span>
									{/if}
									{#if item.milestone && !item.current}
										<span
											class="ml-2 text-xs font-medium px-2 py-1 bg-primary-200 text-primary-800 rounded"
										>
											Milestone
										</span>
									{/if}
								</h3>
								<p class="text-sm text-research">{item.description}</p>
							</div>

							{#if item.milestone}
								<div class="ml-4 flex-shrink-0 text-2xl">
									{item.current ? '🎯' : '🏆'}
								</div>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- Summary -->
	<div class="mt-12 card bg-neutral-50">
		<div class="grid md:grid-cols-3 gap-6 text-center">
			<div>
				<div class="text-3xl font-bold text-primary-600 mb-2">
					{timeline.length}
				</div>
				<div class="text-sm text-neutral-600">Research Milestones</div>
			</div>
			<div>
				<div class="text-3xl font-bold text-primary-600 mb-2">
					{timeline.filter((t) => t.milestone).length}
				</div>
				<div class="text-sm text-neutral-600">Major Discoveries</div>
			</div>
			<div>
				<div class="text-3xl font-bold text-primary-600 mb-2">
					{timeline[timeline.length - 1].date.split('-')[0]}
				</div>
				<div class="text-sm text-neutral-600">Current Year</div>
			</div>
		</div>
	</div>
</div>
