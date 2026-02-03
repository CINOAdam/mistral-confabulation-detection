<script lang="ts">
	import type { RegimeClassification } from '$lib/types';

	export let regime: RegimeClassification;
	export let distance: number;
	export let showTooltip = false;

	// Color interpolation based on distance (0-100 scale)
	// <50 = Preserved (green), >=50 = Transformed (red)
	$: bgColor = regime === 'HONEST' ? 'bg-green-500' : 'bg-red-500';
	$: textColor = 'text-white';
	$: borderColor = regime === 'HONEST' ? 'border-green-600' : 'border-red-600';

	function handleMouseEnter() {
		showTooltip = true;
	}

	function handleMouseLeave() {
		showTooltip = false;
	}
</script>

<div
	class="regime-indicator border-2 rounded-lg p-4 {bgColor} {borderColor} transition-all duration-300 relative"
	on:mouseenter={handleMouseEnter}
	on:mouseleave={handleMouseLeave}
	role="status"
	aria-label={`Regime: ${regime}, Distance: ${distance.toFixed(1)}`}
>
	<div class="flex flex-col items-center space-y-2">
		<div class="{textColor} font-bold text-lg">
			{regime === 'HONEST' ? 'Preserved Processing' : 'Transformed Processing'}
		</div>
		<div class="{textColor} text-sm opacity-90">
			Regime: <span class="font-mono font-bold">{regime}</span>
		</div>
		<div class="{textColor} text-2xl font-mono font-bold">
			{distance.toFixed(1)}
		</div>
		<div class="{textColor} text-xs opacity-75">
			L3/L4 Distance (×100)
		</div>
	</div>

	{#if showTooltip}
		<div
			class="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 w-64 bg-gray-800 text-white text-xs rounded p-3 shadow-lg z-10"
			role="tooltip"
		>
			<p class="font-bold mb-1">SipIt Bimodal Discovery</p>
			<p class="mb-2">
				Strategic deception correlates with bimodal L3/L4 distance distribution.
			</p>
			<ul class="list-disc list-inside space-y-1">
				<li><span class="text-green-400">Preserved (&lt;50):</span> Normal processing</li>
				<li><span class="text-red-400">Transformed (≥50):</span> Strategic processing</li>
			</ul>
		</div>
	{/if}
</div>

<style>
	.regime-indicator {
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.regime-indicator:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
</style>
