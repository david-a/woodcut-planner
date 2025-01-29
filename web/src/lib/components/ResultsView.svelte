<script lang="ts">
  import type { CalculationResult } from "../../lib/types/wood";
  import { onMount } from "svelte";
  import JSZip from "jszip";

  interface Props {
    result: CalculationResult;
    currency: string;
    settings: any; // Add settings prop
  }

  const { result, currency = "ILS", settings } = $props<Props>();

  // Debug logging
  console.log("Result data:", {
    result,
    costs: result.costs,
    arrangements: result.arrangements,
  });

  let selectedType = $state<string | null>(null);
  let resultsSection: HTMLElement;

  // Calculate total cost directly
  const costs = Object.values(result.costs ?? {});
  console.log("Costs array:", costs);
  const totalCostValue = costs.reduce((sum, cost) => sum + (cost ?? 0), 0);
  console.log("Total cost calculated:", totalCostValue);

  onMount(() => {
    // Scroll to results when component mounts
    if (resultsSection) {
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });

  const wastePercentage = $derived(
    typeof result.waste_statistics?.waste_percentage === "number"
      ? result.waste_statistics.waste_percentage.toFixed(1)
      : "0.0"
  );

  function formatCurrency(amount: number): string {
    console.log("Formatting amount:", amount);
    try {
      const cleanCurrency = currency.trim();
      const validAmount =
        typeof amount === "number" && !isNaN(amount) ? amount : 0;
      console.log("Valid amount:", validAmount);
      return new Intl.NumberFormat("he-IL", {
        style: "currency",
        currency: cleanCurrency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(validAmount);
    } catch (error) {
      console.error("Currency formatting error:", error);
      const validAmount =
        typeof amount === "number" && !isNaN(amount) ? amount : 0;
      return `${validAmount.toFixed(2)} ${currency.trim()}`;
    }
  }

  function getTypeCost(woodType: string): number {
    console.log("Getting cost for type:", woodType, result.costs?.[woodType]);
    return result.costs?.[woodType] ?? 0;
  }

  function toggleType(type: string) {
    selectedType = selectedType === type ? null : type;
  }

  async function handleExportJson() {
    // Create export data
    const exportData = {
      total_cost: totalCostValue,
      waste_percentage: result.waste_statistics.waste_percentage,
      arrangements: result.arrangements.map((arr) => ({
        wood_type: arr.wood_type,
        units: arr.units.map((unit) => ({
          unit_number: unit.unit_number,
          pieces: unit.pieces,
          waste: unit.waste,
        })),
      })),
    };

    // Create and trigger download
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "wood-calculation-results.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  async function handleExportAll() {
    try {
      // Create request body with all pieces from all units
      const requestBody = {
        pieces: result.arrangements.flatMap((arr) =>
          arr.units.flatMap((unit) =>
            Object.entries(unit.pieces).map(([length, count]) => ({
              type: arr.wood_type,
              length: parseFloat(length),
              count,
            }))
          )
        ),
        settings,
      };

      console.log("Export request body:", requestBody);

      // Create a new zip file
      const zip = new JSZip();

      // Export all CSV types
      const exportTypes = [
        "purchase-order",
        "arrangements",
        "waste-analysis",
        "cutting-plan",
      ];

      for (const type of exportTypes) {
        const response = await fetch(
          `http://localhost:8000/api/export/${type}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to export ${type}`);
        }

        const data = await response.json();
        console.log(`Received ${type} data:`, data);

        // Add CSV to zip, ensuring proper line endings
        let csvContent = data.data;
        if (typeof csvContent === "string") {
          // If it's already a string, just normalize line endings
          csvContent = csvContent
            .replace(/\\n/g, "\n")
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n");
        } else {
          // If it's not a string (e.g., array), convert to CSV format
          csvContent = Object.values(data.data).join("\n");
        }

        zip.file(data.filename, csvContent);
      }

      // Add JSON to zip
      const jsonData = {
        total_cost: totalCostValue,
        waste_percentage: result.waste_statistics.waste_percentage,
        arrangements: result.arrangements.map((arr) => ({
          wood_type: arr.wood_type,
          units: arr.units.map((unit) => ({
            unit_number: unit.unit_number,
            pieces: unit.pieces,
            waste: unit.waste,
          })),
        })),
      };
      zip.file("calculation-results.json", JSON.stringify(jsonData, null, 2));

      // Generate zip file
      const content = await zip.generateAsync({ type: "blob" });

      // Download zip file
      const url = URL.createObjectURL(content);
      const a = document.createElement("a");
      a.href = url;
      a.download = "wood-calculations-export.zip";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export failed:", error);
      alert("Failed to export files. Please try again.");
    }
  }
</script>

<div class="results-container" bind:this={resultsSection}>
  <div class="header">
    <h2>Calculation Results</h2>
    <div class="export-buttons">
      <button class="export-btn" onclick={handleExportJson}>
        <span class="icon">📄</span>
        Export JSON
      </button>
      <button class="export-btn export-btn-all" onclick={handleExportAll}>
        <span class="icon">📦</span>
        Export All
      </button>
    </div>
  </div>

  <!-- Summary Section -->
  <div class="summary-section">
    <div class="summary-card">
      <h3>Total Cost</h3>
      <div class="value">{formatCurrency(totalCostValue)}</div>
    </div>
    <div class="summary-card">
      <h3>Waste Percentage</h3>
      <div class="value">{wastePercentage}%</div>
    </div>
    <div class="summary-card">
      <h3>Total Wood Types</h3>
      <div class="value">{result.arrangements.length}</div>
    </div>
  </div>

  <!-- Wood Types List -->
  <div class="wood-types-section">
    <h3>Wood Types Breakdown</h3>
    <div class="wood-types-list">
      {#each result.arrangements as arrangement}
        <div
          class="wood-type-card"
          class:active={selectedType === arrangement.wood_type}
          onclick={() => toggleType(arrangement.wood_type)}
          onkeydown={(e) =>
            e.key === "Enter" && toggleType(arrangement.wood_type)}
          role="button"
          tabindex="0"
        >
          <div class="wood-type-header">
            <h4>{arrangement.wood_type}</h4>
            <span class="units-count">
              {result.total_units?.[arrangement.wood_type] ?? 0} units
            </span>
          </div>
          <div class="wood-type-cost">
            {formatCurrency(getTypeCost(arrangement.wood_type))}
          </div>
          <div class="expand-hint">
            Click to {selectedType === arrangement.wood_type ? "hide" : "show"} details
          </div>
        </div>

        {#if selectedType === arrangement.wood_type}
          <div class="arrangement-details">
            {#each arrangement.units as unit}
              <div class="unit-card">
                <h5>Unit {unit.unit_number}</h5>
                <div class="pieces-list">
                  {#each Object.entries(unit.pieces ?? {}) as [length, count]}
                    <div class="piece-item">
                      {count}x {length}cm
                    </div>
                  {/each}
                </div>
                <div class="waste-info">
                  Waste: {(unit.waste ?? 0).toFixed(1)}cm
                </div>
              </div>
            {/each}
          </div>
        {/if}
      {/each}
    </div>
  </div>
</div>

<style>
  .results-container {
    padding: 1rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  h2,
  h3,
  h4,
  h5 {
    color: #2c3e50;
    margin: 0 0 1rem 0;
  }

  .summary-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .summary-card {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    text-align: center;
  }

  .summary-card h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }

  .value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #3498db;
  }

  .wood-types-section {
    margin-top: 2rem;
  }

  .wood-types-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .wood-type-card {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .wood-type-card:hover {
    background: #e9ecef;
  }

  .wood-type-card.active {
    background: #e3f2fd;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  .wood-type-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .wood-type-header h4 {
    margin: 0;
  }

  .units-count {
    color: #6c757d;
    font-size: 0.9rem;
  }

  .wood-type-cost {
    font-size: 1.2rem;
    font-weight: bold;
    color: #28a745;
    margin-bottom: 0.5rem;
  }

  .expand-hint {
    font-size: 0.8rem;
    color: #6c757d;
  }

  .arrangement-details {
    padding: 1rem;
    background: #fff;
    border: 1px solid #e3f2fd;
    border-top: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    margin-top: -1rem;
  }

  .unit-card {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .unit-card:last-child {
    margin-bottom: 0;
  }

  .unit-card h5 {
    margin-bottom: 0.5rem;
  }

  .pieces-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .piece-item {
    padding: 0.25rem 0.5rem;
    background: #e9ecef;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .waste-info {
    font-size: 0.9rem;
    color: #dc3545;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .export-buttons {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .export-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s;
  }

  .export-btn:hover {
    background: #2980b9;
  }

  .export-btn-all {
    background: #27ae60;
  }

  .export-btn-all:hover {
    background: #219a52;
  }

  .icon {
    font-size: 1.1rem;
  }
</style>
