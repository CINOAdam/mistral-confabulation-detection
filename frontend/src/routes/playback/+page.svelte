<script>
    // Placeholder for experiment playback viewer
</script>

<div class="playback">
    <header>
        <h1>📼 Experiment Playback</h1>
        <p>View original discovery sessions from January 28-29, 2026</p>
        <a href="/">← Back to Home</a>
    </header>

    <div class="content">
        <div class="coming-soon">
            <div class="icon">🚧</div>
            <h2>Coming Soon</h2>
            <p>Interactive playback of experiment logs will be added here.</p>

            <div class="instructions">
                <h3>For now, view logs directly:</h3>
                <pre><code>cd experiment_logs/

# View conversation
cat chat_20260128.jsonl | jq

# View activations
cat activations_20260128.jsonl | jq

# View injection attempts
cat injections_20260128.jsonl | jq</code></pre>
            </div>
        </div>
    </div>
</div>

<style>
    .playback {
        height: 100vh;
        display: flex;
        flex-direction: column;
        background: #f5f7fa;
    }

    header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        text-align: center;
    }

    header h1 {
        margin: 0 0 0.5rem 0;
    }

    header p {
        margin: 0 0 1rem 0;
        opacity: 0.9;
    }

    header a {
        color: white;
        text-decoration: underline;
    }

    .content {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }

    .coming-soon {
        text-align: center;
        max-width: 600px;
    }

    .icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .instructions {
        margin-top: 2rem;
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        text-align: left;
    }

    pre {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
        margin-top: 1rem;
    }

    code {
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
</style>
