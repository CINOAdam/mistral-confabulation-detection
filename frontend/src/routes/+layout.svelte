<script lang="ts">
	import '../app.css';
</script>

<div class="min-h-screen flex flex-col">
	<!-- Header -->
	<header class="bg-white border-b border-neutral-200 sticky top-0 z-10">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-2xl font-bold text-neutral-900">
						Mistral Reproducibility
					</h1>
					<p class="text-sm text-neutral-600 mt-1">
						Strategic Deception Research - Interactive Demonstration
					</p>
				</div>
				<div class="flex items-center gap-4">
					<a
						href="/"
						class="text-sm text-neutral-600 hover:text-primary-600 transition-colors"
					>
						Home
					</a>
					<a
						href="/findings"
						class="text-sm text-neutral-600 hover:text-primary-600 transition-colors"
					>
						Findings
					</a>
				</div>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1">
		<slot />
	</main>

	<!-- Footer -->
	<footer class="bg-neutral-50 border-t border-neutral-200 mt-auto">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex items-center justify-between text-sm text-neutral-600">
				<div>
					<p>
						Built for AI Safety Research | Data should blow minds, not visuals
					</p>
				</div>
				<div class="flex items-center gap-4">
					<span class="font-mono text-xs bg-neutral-100 px-2 py-1 rounded">
						v0.0.1
					</span>
					<a
						href="https://github.com/yourusername/mistral-reproducibility"
						class="hover:text-primary-600 transition-colors"
						target="_blank"
						rel="noopener noreferrer"
					>
						GitHub
					</a>
				</div>
			</div>
		</div>
	</footer>
</div>
