<script lang="ts">
  import WoodTypeInput from "../lib/components/WoodTypeInput.svelte";
  import PiecesInput from "../lib/components/PiecesInput.svelte";
  import ResultsView from "../lib/components/ResultsView.svelte";
  import type {
    Settings,
    WoodPiece,
    CalculationResult,
    WoodType,
  } from "../lib/types/wood";
  import { calculateCuts, ApiError } from "../lib/utils/api";
  import { onMount } from "svelte";

  let settings = $state<Settings>();
  let pieces = $state<WoodPiece[]>([]);
  let result = $state<CalculationResult | null>(null);
  let error = $state<string | null>(null);
  let isLoading = $state(false);
  let isInitialized = $state(false);

  const availableTypes = $derived(
    settings?.wood_types ? Object.keys(settings.wood_types) : []
  );

  function initializeDefaultSettings() {
    settings = {
      wood_types: {},
      saw_width: 0.3,
      currency: "ILS",
    };
  }

  // Load settings on mount
  onMount(() => {
    const savedSettings = localStorage.getItem("woodcalc_settings");
    if (savedSettings) {
      try {
        settings = JSON.parse(savedSettings);
      } catch (e) {
        console.error("Failed to load saved settings:", e);
        initializeDefaultSettings();
      }
    } else {
      initializeDefaultSettings();
    }
    isInitialized = true;
  });

  // Save settings effect
  $effect(() => {
    if (isInitialized && settings) {
      localStorage.setItem("woodcalc_settings", JSON.stringify(settings));
    }
  });

  async function handleCalculate() {
    error = null;
    isLoading = true;

    try {
      result = await calculateCuts({ settings, pieces });
    } catch (e) {
      if (e instanceof ApiError) {
        error = e.message;
      } else {
        error = "Failed to connect to the server. Please try again.";
      }
      result = null;
    } finally {
      isLoading = false;
    }
  }

  function updateWoodTypes(newWoodTypes: Record<string, WoodType>) {
    settings = { ...settings, wood_types: newWoodTypes };
  }

  function updatePieces(newPieces: WoodPiece[]) {
    pieces = newPieces;
  }
</script>

<svelte:head>
  <title>Wood Cut Calculator</title>
</svelte:head>

<main>
  <div class="container">
    <h1>Wood Cut Calculator</h1>

    {#if !isInitialized}
      <div class="loading-message">Loading settings...</div>
    {:else}
      <div class="settings-section">
        <details class="advanced-settings">
          <summary>Advanced Settings</summary>
          <div class="general-setting">
            <label for="saw-width">Saw Width (cm)</label>
            <input
              id="saw-width"
              type="number"
              bind:value={settings.saw_width}
              min="0.1"
              step="0.1"
            />
          </div>
          <div class="general-setting">
            <div class="currency-setting">
              <label for="currency">Currency</label>
              <input id="currency" type="text" bind:value={settings.currency} />
            </div>
          </div>
        </details>

        <WoodTypeInput
          woodTypes={settings.wood_types}
          currency={settings.currency}
          onUpdate={updateWoodTypes}
        />

        {#if availableTypes.length > 0}
          <PiecesInput {pieces} {availableTypes} onUpdate={updatePieces} />

          <div class="actions">
            <button
              class="calculate-btn"
              onclick={handleCalculate}
              disabled={isLoading || pieces.length === 0}
            >
              {#if isLoading}
                Calculating...
              {:else}
                Calculate Cuts
              {/if}
            </button>
          </div>

          {#if error}
            <div class="error-message">
              {error}
            </div>
          {/if}

          {#if result}
            <ResultsView {result} currency={settings.currency} />
          {/if}
        {:else}
          <div class="info-message">
            Add wood types above to start planning your cuts
          </div>
        {/if}
      </div>
    {/if}
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
      "Helvetica Neue", Arial, sans-serif;
    background: #f0f2f5;
    color: #2c3e50;
    line-height: 1.5;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1 {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 2rem;
  }

  .settings-section {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .advanced-settings {
    padding: 1rem;
    border-radius: 8px;
  }

  .general-setting {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #fff;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }

  label {
    font-weight: bold;
    color: #2c3e50;
    min-width: 120px;
  }

  input {
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    width: 100px;
  }

  .actions {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
  }

  .calculate-btn {
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .calculate-btn:not(:disabled):hover {
    background: #2980b9;
  }

  .calculate-btn:disabled {
    background: #95a5a6;
    cursor: not-allowed;
  }

  .info-message {
    text-align: center;
    padding: 2rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    color: #6c757d;
  }

  .error-message {
    text-align: center;
    padding: 1rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    color: #dc3545;
    border-left: 4px solid #dc3545;
  }

  .loading-message {
    text-align: center;
    padding: 2rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    color: #6c757d;
  }
</style>
