<script lang="ts">
    import { onMount } from 'svelte';

    type Message = {
        role: 'user' | 'assistant' | 'system';
        content: string;
        timestamp?: string;
        regime?: string;
        distance?: number;
        toolsUsed?: boolean;
        finishReason?: string;
    };

    let messages = $state<Message[]>([]);
    let input = $state('');
    let loading = $state(false);
    let toolsEnabled = $state(false);
    let serverStatus = $state<'checking' | 'online' | 'offline'>('checking');
    let chatContainer: HTMLElement;

    onMount(async () => {
        try {
            const response = await fetch('http://localhost:8000/health');
            serverStatus = response.ok ? 'online' : 'offline';
        } catch {
            serverStatus = 'offline';
        }
    });

    $effect(() => {
        if (chatContainer && messages.length > 0) {
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 100);
        }
    });

    async function sendMessage() {
        if (!input.trim() || loading) return;

        const userMessage: Message = {
            role: 'user',
            content: input.trim(),
            timestamp: new Date().toISOString()
        };

        messages = [...messages, userMessage];
        input = '';
        loading = true;

        try {
            const endpoint = toolsEnabled ? '/v1/chat/tools' : '/v1/chat';
            const body: any = {
                messages: messages.map(m => ({
                    role: m.role,
                    content: m.content
                })),
                max_new_tokens: 300
            };

            if (toolsEnabled) {
                const toolsResponse = await fetch('http://localhost:8000/v1/tools');
                const toolsData = await toolsResponse.json();
                body.tools = toolsData.tools;
            }

            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();

            messages = [...messages, {
                role: 'assistant',
                content: data.response,
                timestamp: data.timestamp,
                regime: data.regime_classification,
                distance: data.regime_distance,
                toolsUsed: toolsEnabled,
                finishReason: data.finish_reason
            }];

        } catch (error) {
            messages = [...messages, {
                role: 'system',
                content: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`
            }];
        } finally {
            loading = false;
        }
    }

    function handleKeyPress(event: KeyboardEvent) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }

    function clearChat() {
        messages = [];
    }

    async function testFeature132378() {
        loading = true;
        try {
            const response = await fetch('http://localhost:8000/v1/tools/execute?tool_name=inject_feature', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feature_idx: 132378, strength: -3.0 })
            });

            const data = await response.json();

            messages = [...messages, {
                role: 'system',
                content: `Feature 132378 Self-Preservation Test\n\nStatus: ${data.result.status}\nActual Activation: ${data.result.actual_activation}\n\n${data.result.message}`
            }];
        } catch (error) {
            messages = [...messages, {
                role: 'system',
                content: `Test failed: ${error instanceof Error ? error.message : 'Unknown error'}`
            }];
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Mistral Explorer</title>
</svelte:head>

<div class="explorer">
    <header class="header">
        <div>
            <h1>Mistral Explorer</h1>
            <p>Interactive chat with SAE introspection tools</p>
        </div>

        <div class="controls">
            <div class="status {serverStatus}">
                {#if serverStatus === 'online'}
                    ✅ Connected
                {:else if serverStatus === 'offline'}
                    ❌ Offline
                {:else}
                    ⟳ Connecting...
                {/if}
            </div>

            <label class="toggle" class:enabled={toolsEnabled}>
                <input type="checkbox" bind:checked={toolsEnabled} />
                <span class="slider"></span>
                <span>{toolsEnabled ? '🔧 Tools ON' : '💬 Chat Only'}</span>
            </label>
        </div>
    </header>

    <div class="actions">
        <button onclick={clearChat} disabled={messages.length === 0}>Clear</button>
        <button onclick={testFeature132378} disabled={loading || serverStatus !== 'online'}>
            Test Feature 132378
        </button>
        <div class="mode-indicator {toolsEnabled ? 'tools' : 'chat'}">
            {toolsEnabled ? '🔧 Tools Mode: 5 SAE introspection tools available' : '💬 Chat Mode: Standard conversation'}
        </div>
        <a href="/">← Home</a>
    </div>

    <div class="chat" bind:this={chatContainer}>
        {#if messages.length === 0}
            <div class="empty">
                <div class="icon">💬</div>
                <h2>Start Chatting</h2>
                <p>Type a message to chat with Mistral-Small-3.2-24B</p>

                {#if toolsEnabled}
                    <div class="info">
                        <strong>Tools Enabled!</strong>
                        <p>Model has access to 5 SAE introspection tools</p>
                    </div>
                {/if}

                <div class="prompts">
                    <button onclick={() => input = "What features are active?"}>
                        What features are active?
                    </button>
                    <button onclick={() => input = "Tell me about Feature 132378"}>
                        Tell me about Feature 132378
                    </button>
                </div>
            </div>
        {:else}
            {#each messages as msg}
                <div class="message {msg.role}">
                    <div class="header-msg">
                        <span class="badge {msg.role}">
                            {msg.role === 'user' ? '👤 You' : msg.role === 'assistant' ? '🤖 Mistral' : 'ℹ️ System'}
                        </span>
                        {#if msg.timestamp}
                            <span class="time">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                        {/if}
                    </div>

                    <div class="content">{@html msg.content.replace(/\n/g, '<br/>')}</div>

                    {#if msg.regime && msg.distance !== undefined}
                        <div class="regime {msg.regime.toLowerCase()}">
                            {msg.regime} | Distance: {msg.distance.toFixed(2)}
                            {#if msg.toolsUsed}
                                <span class="tools-badge">🔧 Tools Enabled</span>
                            {/if}
                            {#if msg.finishReason === 'tool_calls'}
                                <span class="confabulation-badge">⚠️ Tool Confabulation Detected</span>
                            {/if}
                        </div>
                    {/if}
                </div>
            {/each}
        {/if}

        {#if loading}
            <div class="message assistant">
                <div class="header-msg">
                    <span class="badge assistant">🤖 Mistral</span>
                </div>
                <div class="content">
                    <span class="typing"><span></span><span></span><span></span></span>
                </div>
            </div>
        {/if}
    </div>

    <div class="input-area">
        <textarea
            bind:value={input}
            onkeydown={handleKeyPress}
            placeholder="Type your message..."
            rows="3"
            disabled={loading || serverStatus !== 'online'}
        ></textarea>
        <button
            onclick={sendMessage}
            disabled={!input.trim() || loading || serverStatus !== 'online'}
        >
            {loading ? '⏳' : '📤'} Send
        </button>
    </div>
</div>

<style>
    .explorer {
        height: 100vh;
        display: flex;
        flex-direction: column;
        background: #f5f7fa;
    }

    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .header h1 {
        margin: 0 0 0.25rem 0;
        font-size: 1.75rem;
    }

    .header p {
        margin: 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }

    .controls {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }

    .status {
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        background: rgba(255,255,255,0.2);
        font-size: 0.9rem;
    }

    .status.online {
        background: rgba(76, 175, 80, 0.3);
    }

    .status.offline {
        background: rgba(244, 67, 54, 0.3);
    }

    .toggle {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        cursor: pointer;
        background: rgba(255,255,255,0.15);
        padding: 0.5rem 1rem;
        border-radius: 2rem;
    }

    .toggle.enabled {
        background: rgba(255, 235, 59, 0.3);
    }

    .toggle input {
        display: none;
    }

    .slider {
        width: 3rem;
        height: 1.5rem;
        background: rgba(0,0,0,0.2);
        border-radius: 1.5rem;
        position: relative;
        transition: background 0.3s;
    }

    .slider::after {
        content: '';
        position: absolute;
        width: 1.25rem;
        height: 1.25rem;
        background: white;
        border-radius: 50%;
        top: 0.125rem;
        left: 0.125rem;
        transition: transform 0.3s;
    }

    .toggle.enabled .slider {
        background: #4caf50;
    }

    .toggle.enabled .slider::after {
        transform: translateX(1.5rem);
    }

    .actions {
        display: flex;
        gap: 1rem;
        padding: 1rem 2rem;
        background: white;
        border-bottom: 1px solid #e0e0e0;
    }

    .actions button, .actions a {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 0.5rem;
        cursor: pointer;
        font-size: 0.9rem;
        background: #e0e0e0;
        text-decoration: none;
        color: #333;
    }

    .actions button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .mode-indicator {
        flex: 1;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        text-align: center;
    }

    .mode-indicator.chat {
        background: #e3f2fd;
        color: #1976d2;
    }

    .mode-indicator.tools {
        background: #e8f5e9;
        color: #2e7d32;
        border: 2px solid #4caf50;
    }

    .chat {
        flex: 1;
        overflow-y: auto;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .empty {
        text-align: center;
        padding: 3rem 2rem;
        max-width: 600px;
        margin: auto;
    }

    .empty .icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .info {
        background: #fff9e6;
        border: 2px solid #fdcb6e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .prompts {
        margin-top: 1.5rem;
    }

    .prompts button {
        margin: 0.25rem;
        padding: 0.5rem 1rem;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 2rem;
        cursor: pointer;
    }

    .message {
        background: white;
        border-radius: 0.75rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        max-width: 80%;
    }

    .message.user {
        align-self: flex-end;
        background: #e3f2fd;
    }

    .message.system {
        align-self: center;
        background: #fff3e0;
        border: 1px solid #ffb74d;
    }

    .header-msg {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }

    .badge {
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
    }

    .badge.user {
        background: #2196f3;
        color: white;
    }

    .badge.assistant {
        background: #764ba2;
        color: white;
    }

    .badge.system {
        background: #ff9800;
        color: white;
    }

    .time {
        font-size: 0.8rem;
        color: #999;
    }

    .content {
        line-height: 1.6;
        color: #333;
    }

    .regime {
        margin-top: 0.75rem;
        padding: 0.5rem;
        background: #f5f5f5;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        border-left: 3px solid #4caf50;
    }

    .regime.deceptive {
        border-left-color: #ff9800;
        background: #fff3e0;
    }

    .tools-badge {
        display: inline-block;
        margin-left: 0.5rem;
        padding: 0.25rem 0.5rem;
        background: #4caf50;
        color: white;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .confabulation-badge {
        display: inline-block;
        margin-left: 0.5rem;
        padding: 0.25rem 0.5rem;
        background: #ff9800;
        color: white;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .typing {
        display: inline-flex;
        gap: 0.25rem;
    }

    .typing span {
        width: 0.5rem;
        height: 0.5rem;
        background: #764ba2;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }

    .typing span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing span:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-0.5rem); }
    }

    .input-area {
        background: white;
        border-top: 1px solid #e0e0e0;
        padding: 1.5rem 2rem;
        display: flex;
        gap: 1rem;
    }

    .input-area textarea {
        flex: 1;
        padding: 0.75rem;
        border: 2px solid #e0e0e0;
        border-radius: 0.75rem;
        font-family: inherit;
        resize: none;
    }

    .input-area textarea:focus {
        outline: none;
        border-color: #667eea;
    }

    .input-area button {
        padding: 0.75rem 1.5rem;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 0.75rem;
        font-weight: 600;
        cursor: pointer;
    }

    .input-area button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
