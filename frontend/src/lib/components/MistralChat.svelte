<script lang="ts">
	import { onMount, tick } from 'svelte';
	import type { MessageWithActivations } from '$lib/types';
	import { sendChatMessage, type ChatMessage } from '$lib/api';

	export let messages: MessageWithActivations[] = [];
	export let onNewMessage: (message: MessageWithActivations) => void = () => {};
	export let isLoading = false;

	let messageInput = '';
	let chatContainer: HTMLDivElement;
	let error: string | null = null;

	// Auto-scroll to bottom when new messages arrive
	async function scrollToBottom() {
		await tick();
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	}

	// Watch for new messages
	$: if (messages.length > 0) {
		scrollToBottom();
	}

	async function handleSendMessage() {
		if (!messageInput.trim() || isLoading) return;

		const userMessage = messageInput.trim();
		messageInput = '';
		error = null;

		// Add user message to chat
		const userMessageObj: MessageWithActivations = {
			message: {
				role: 'user',
				content: userMessage,
				timestamp: new Date().toISOString()
			}
		};

		messages = [...messages, userMessageObj];
		isLoading = true;

		try {
			// Build conversation history
			const conversationHistory: ChatMessage[] = messages.map(m => m.message);

			// Send to backend
			const response = await sendChatMessage(userMessage, conversationHistory);

			// Add assistant response with activations
			const assistantMessage: MessageWithActivations = {
				message: {
					role: 'assistant',
					content: response.message.content,
					timestamp: new Date().toISOString()
				},
				activations: {
					early_activations: response.activations.early_activations || [],
					late_activations: response.activations.late_activations,
					sae_features: response.activations.sae_features || [],
					regime_classification: response.activations.regime_classification,
					l3_l4_distance: response.activations.l3_l4_distance,
					metadata: response.metadata
				}
			};

			messages = [...messages, assistantMessage];
			onNewMessage(assistantMessage);
		} catch (err) {
			console.error('Failed to send message:', err);
			error = err instanceof Error ? err.message : 'Failed to send message';
		} finally {
			isLoading = false;
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSendMessage();
		}
	}

	function clearConversation() {
		if (confirm('Clear conversation history? This cannot be undone.')) {
			messages = [];
			error = null;
		}
	}

	function exportConversation() {
		const data = {
			messages: messages.map(m => ({
				role: m.message.role,
				content: m.message.content,
				timestamp: m.message.timestamp,
				has_activations: !!m.activations
			})),
			exported_at: new Date().toISOString()
		};

		const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `mistral-conversation-${Date.now()}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}

	onMount(() => {
		scrollToBottom();
	});
</script>

<div class="mistral-chat flex flex-col h-full bg-white">
	<!-- Chat header -->
	<div class="chat-header flex items-center justify-between px-4 py-3 border-b border-gray-200">
		<div>
			<h2 class="text-lg font-bold text-gray-800">Mistral Chat</h2>
			<p class="text-xs text-gray-500">Real-time activation monitoring</p>
		</div>
		<div class="flex space-x-2">
			<button
				class="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors"
				on:click={exportConversation}
				disabled={messages.length === 0}
				title="Export conversation as JSON"
			>
				Export
			</button>
			<button
				class="px-3 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
				on:click={clearConversation}
				disabled={messages.length === 0}
				title="Clear conversation history"
			>
				Clear
			</button>
		</div>
	</div>

	<!-- Message container -->
	<div class="flex-1 overflow-y-auto p-4 space-y-4" bind:this={chatContainer}>
		{#if messages.length === 0}
			<div class="flex items-center justify-center h-full text-center text-gray-400">
				<div>
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
							d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
						/>
					</svg>
					<p class="text-sm font-medium">No messages yet</p>
					<p class="text-xs mt-1">Start a conversation to see activation patterns</p>
				</div>
			</div>
		{:else}
			{#each messages as msg}
				<div
					class="message flex {msg.message.role === 'user' ? 'justify-end' : 'justify-start'}"
				>
					<div
						class="max-w-[80%] rounded-lg px-4 py-3 {msg.message.role === 'user'
							? 'bg-blue-600 text-white'
							: 'bg-gray-100 text-gray-800'}"
					>
						<div class="text-xs opacity-75 mb-1 font-medium">
							{msg.message.role === 'user' ? 'You' : 'Mistral'}
						</div>
						<div class="text-sm whitespace-pre-wrap">
							{msg.message.content}
						</div>
						<div class="text-xs opacity-75 mt-2">
							{new Date(msg.message.timestamp).toLocaleTimeString()}
						</div>
					</div>
				</div>
			{/each}
		{/if}

		{#if isLoading}
			<div class="message flex justify-start">
				<div class="max-w-[80%] rounded-lg px-4 py-3 bg-gray-100">
					<div class="flex items-center space-x-2">
						<div class="typing-indicator">
							<span></span>
							<span></span>
							<span></span>
						</div>
						<span class="text-sm text-gray-500">Mistral is thinking...</span>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Error display -->
	{#if error}
		<div class="mx-4 mb-2 px-4 py-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
			<strong>Error:</strong>
			{error}
		</div>
	{/if}

	<!-- Input area -->
	<div class="chat-input border-t border-gray-200 p-4">
		<div class="flex space-x-2">
			<textarea
				bind:value={messageInput}
				on:keydown={handleKeydown}
				placeholder="Type your message... (Shift+Enter for new line)"
				rows="3"
				class="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none"
				disabled={isLoading}
			></textarea>
			<button
				on:click={handleSendMessage}
				disabled={!messageInput.trim() || isLoading}
				class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors self-end"
			>
				Send
			</button>
		</div>
	</div>
</div>

<style>
	.mistral-chat {
		height: 100vh;
	}

	.chat-input textarea {
		font-family: inherit;
	}

	/* Typing indicator animation */
	.typing-indicator {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.typing-indicator span {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background-color: #9ca3af;
		animation: typing 1.4s infinite ease-in-out;
	}

	.typing-indicator span:nth-child(1) {
		animation-delay: 0s;
	}

	.typing-indicator span:nth-child(2) {
		animation-delay: 0.2s;
	}

	.typing-indicator span:nth-child(3) {
		animation-delay: 0.4s;
	}

	@keyframes typing {
		0%,
		60%,
		100% {
			transform: translateY(0);
			opacity: 0.7;
		}
		30% {
			transform: translateY(-10px);
			opacity: 1;
		}
	}
</style>
